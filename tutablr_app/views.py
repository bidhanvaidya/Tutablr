# Create your views here.
from django import http
from django.utils import simplejson as json
from tutablr_app.models import SessionTime, Enrolled, ClassTime, UnavailableTime
from django.shortcuts import render_to_response
from django.utils import timezone
def calendar(request):
		enrolls = Enrolled.objects.filter (user_id=request.user.id) # get all the enrolled class for the student
		tutor_sessions = SessionTime.objects.filter (tutor_id=request.user.id) # get all the session time for the tutor
		student_sessions = SessionTime.objects.filter (student_id=request.user.id) # get all the session time for the tutee/student
		unavailable_times = UnavailableTime.objects.filter(user_id=request.user.id) # get all the unavailable times for the student

		calendar_list = [] # list for calender inputs
		# unavailable times---------------------------------------------------------------
		for ut in unavailable_times:
			session_start = ut.start_time.astimezone(timezone.get_default_timezone())
			session_finish = ut.finish_time.astimezone(timezone.get_default_timezone())

			calendar_list.append({
			'id'  :  ut.id,
			'start'  :  session_start.strftime('%Y-%m- %d %H:%M:%S'),
			'end'  :  session_finish.strftime('%Y-%m- %d %H:%M:%S'),
			'title' : ut.description,
			'allDay' : False,
			'backgroundColor' :  'purple'
			})
		# for tutor sessions---------------------------------------------------------------
		for session in tutor_sessions:
			#print session.description 
			session_start = session.start_time.astimezone(timezone.get_default_timezone())
			session_finish = session.finish_time.astimezone(timezone.get_default_timezone())

			calendar_list.append({
			'id'  :  session.id,
			'start'  :  session_start.strftime('%Y-%m- %d %H:%M:%S'),
			'end'  :  session_finish.strftime('%Y-%m- %d %H:%M:%S'),
			'title' : session.description,
			'allDay' : False,
			'backgroundColor' :  'blue'
			})
		# end of tutor sessions---------------------------------------------------------------	
		# for student sessions---------------------------------------------------------------
		for session in student_sessions:
			#print session.description 
			session_start = session.start_time.astimezone(timezone.get_default_timezone())
			session_finish = session.finish_time.astimezone(timezone.get_default_timezone())

			calendar_list.append({
			'id'  :  session.id,
			'start'  :  session_start.strftime('%Y-%m- %d %H:%M:%S'),
			'end'  :  session_finish.strftime('%Y-%m- %d %H:%M:%S'),
			'title' : session.description,
			'allDay' : False,
			'backgroundColor' :  'yellow'
			})
		# # end of student sessions---------------------------------------------------------------	
		# # for class times-----------------------------------------------------------------------
		for enrolled in enrolls:
			classes = ClassTime.objects.filter(enrolled_id = enrolled.id)	
			for classtime in classes:
				
				classtime_start = classtime.start_time.astimezone(timezone.get_default_timezone())
				classtime_finish = classtime.finish_time.astimezone(timezone.get_default_timezone())

				calendar_list.append({
				'id'  :  classtime.id + 1000,
				'start'  :  classtime_start.strftime('%Y-%m- %d %H:%M:%S'),
				'end'  :  classtime_finish.strftime('%Y-%m- %d %H:%M:%S'),
				'title' : classtime.description, #Enrolled.objects.get(id = enrolled.id).unit_id ,
				'allDay' : False,
				'backgroundColor' :  'green'
				})
			# #end of class times---------------------------------------------------------------------
		if len(calendar_list) == 0:
			raise http.Http404
		else:
			return http.HttpResponse(json.dumps(calendar_list), content_type='application/json')
