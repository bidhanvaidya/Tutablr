# Create your views here.
from django import http
from django.utils import simplejson as json
from tutablr_app.models import SessionTime, Enrolled, ClassTime, UnavailableTime, Booking
from django.shortcuts import render_to_response
from django.utils import timezone

def calendar(request):
		enrolls = Enrolled.objects.filter (user_id=request.user.id) # get all the enrolled class for the student
		tutor_sessions = SessionTime.objects.filter (tutor_id=request.user.id) # get all the session time for the tutor
		student_sessions = SessionTime.objects.filter (student_id=request.user.id) # get all the session time for the tutee/student
		unavailable_times = UnavailableTime.objects.filter(user_id=request.user.id) # get all the unavailable times for the student
		tutor_bookings = Booking.objects.filter(tutor_id=request.user.id, is_rejected=False, is_confirmed=False)
		student_bookings = Booking.objects.filter(student_id=request.user.id, is_rejected=False, is_confirmed = False)
		calendar_list = [] # list for calender inputs
		#pending bookings-------------------------------------------------------------------
		for booking in tutor_bookings:
			booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
			booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
			calendar_list.append({
			'id'  :  booking.id,
			'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : booking.description,
			'allDay' : False,
			'backgroundColor' :  'blue',
			'borderColor' : 'red',
			'editable' : True,
			'type' : 'tutor_booking'
			})
		for booking in student_bookings:
			booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
			booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())

			calendar_list.append({
			'id'  :  booking.id,
			'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : booking.description,
			'allDay' : False,
			'textColor' : 'black',
			'backgroundColor' :  'yellow',
			'borderColor' : 'red',
			'editable' : True,
			'type' : 'student_booking'
			})
		# unavailable times---------------------------------------------------------------
		for ut in unavailable_times:
			session_start = ut.start_time.astimezone(timezone.get_default_timezone())
			session_finish = ut.finish_time.astimezone(timezone.get_default_timezone())

			calendar_list.append({
			'id'  :  ut.id,
			'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : ut.description,
			'allDay' : False,
			'backgroundColor' :  'purple',
			'editable' : True,
			'type' : 'unavailable'
			})
		# for tutor sessions---------------------------------------------------------------
		for session in tutor_sessions:
			session_start = session.start_time.astimezone(timezone.get_default_timezone())
			session_finish = session.finish_time.astimezone(timezone.get_default_timezone())

			calendar_list.append({
			'id'  :  session.id,
			'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : session.description,
			'allDay' : False,
			'backgroundColor' :  'blue',
			'editable' : True,
			'type:' : 'tutor_session'
			})
		# end of tutor sessions---------------------------------------------------------------	
		# for student sessions---------------------------------------------------------------
		for session in student_sessions:
			session_start = session.start_time.astimezone(timezone.get_default_timezone())
			session_finish = session.finish_time.astimezone(timezone.get_default_timezone())

			calendar_list.append({
			'id'  :  session.id,
			'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : session.description,
			'allDay' : False,
			'textColor' : 'black',
			'backgroundColor' :  'yellow',
			'editable' : True,
			'type' : 'student_session'
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
				'start'  :  classtime_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  classtime_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : classtime.description, #Enrolled.objects.get(id = enrolled.id).unit_id ,
				'allDay' : False,
				'backgroundColor' :  'green',
				'editable' : False,
				'type' : 'class'
				})
			# #end of class times---------------------------------------------------------------------
		if len(calendar_list) == 0:
			raise http.Http404
		else:
			return http.HttpResponse(json.dumps(calendar_list), content_type='application/json')
			
	
def delete(request, id):
	if request.method == 'POST': 
		user_id = request.user.id
		if request.POST.get('type', None) == 'tutor_booking' or request.POST.get('type', None) == 'student_booking':
			booking = Booking.objects.filter(pk=id)
			if booking.tutor_id == user_id or booking.student_id == user_id:
				booking.delete()
				return http.HttpResponse('deleted')
			else:
				raise http.Http404
		elif request.POST.get('type') == 'unavailable':
			unavailable = UnavailableTime.objects.filter(pk=id)
			if unavailable.user_id==user_id:
				unavailable.delete()
				return http.HttpResponse('deleted')
			else:
				raise http.Http404
		elif request.POST.get('type') == 'student_session' or request.POST.get('type') == 'tutor_session':
			session = SessionTime.objects.filter(pk=id)
			if session.tutor_id == user_id or session.student_id == user_id:
				session.delete()
				return http.HttpResponse('deleted')
			else:
				raise http.Http404
	else:
		raise http.Http404
		
def update(request, id):
	if request.method == 'POST': 
		user_id = request.user.id			
		if request.POST.get('type') == 'tutor_booking' or request.POST.get('type') == 'student_booking':
			booking = Booking.objects.filter(pk=id)
			if booking.tutor_id == user_id or booking.student_id == user_id:
				booking.description = request.POST.get('description')
				booking.start_time = request.POST.get('start_time')
				booking.finish_time = request.POST.get('finish_time')
				booking.is_rejected = request.POST.get('is_rejected')
				booking.is_confirmed = request.POST.get('is_confirmed')
				booking.save()
				return http.HttpResponse('updated')
			else:
				raise http.Http404
		elif request.POST.get('type') == 'unavailable':
			unavailable = UnavailableTime.objects.filter(pk=id)
			if unavailable.user_id==user_id:
				description = request.POST.get('description')
				booking.start_time = request.POST.get('start_time')
				booking.finish_time = request.POST.get('finish_time')
				unavailable.save()
				return http.HttpResponse('updated')
			else:
				raise http.Http404
		elif request.POST.get('type') == 'student_session' or request.POST.get('type') == 'tutor_session':
			session = SessionTime.objects.filter(pk=id)
			if session.tutor_id == user_id or session.student_id == user_id:
				description = request.POST.get('description')
				start_time = request.POST.get('start_time')
				finish_time = request.POST.get('finish_time')
				session.save()
				return http.HttpResponse('updated')
			else:
				raise http.Http404
	else:
		raise http.Http404
def add(request):
	if request.method == 'POST': 
		user_id = request.user.id
		if request.POST.get('type') == 'tutor_booking':
			booking = Booking(tutor_id = user_id, 
				student_id = request.POST.get('student_id'), 
				description = request.POST.get('description'),
				start_time = request.POST.get('start_time'),
				finish_time = request.POST.get('finish_time'),
				unit_id = request.POST.get('unit_id'),
				is_rejected = False,
				is_confirmed = False
				)
			booking.save()
			return http.HttpResponse('added')
		elif request.POST.get('type') == 'student_booking':
			booking = Booking(tutor_id = request.POST.get('tutor_id'), 
				student_id = user_id, 
				description = request.POST.get('description'),
				start_time = request.POST.get('start_time'),
				finish_time = request.POST.get('finish_time'),
				unit_id = request.POST.get('unit_id'),
				is_rejected = False,
				is_confirmed = False
				)
			booking.save()
			return http.HttpResponse('added')
		elif request.POST.get('type') == 'unavailable':
			unavailable = UnavailableTime(user_id = user_id, 
				description = request.POST.get('description'),
				start_time = request.POST.get('start_time'),
				finish_time = request.POST.get('finish_time'),
				)
			unavailable.save()
			return http.HttpResponse('added')
		elif request.POST.get('type') == 'student_session':
			session = SessionTime(tutor_id = request.POST.get('tutor_id'), 
				student_id = user_id, 
				description = request.POST.get('description'),
				start_time = request.POST.get('start_time'),
				finish_time = request.POST.get('finish_time'),
				unit_id = request.POST.get('unit_id'),
				)
			session.save()
			return http.HttpResponse('added')
		elif request.POST.get('type') == 'tutor_session':
			session = SessionTime(tutor_id = user_id, 
				student_id = request.POST.get('student_id'), 
				description = request.POST.get('description'),
				start_time = request.POST.get('start_time'),
				finish_time = request.POST.get('finish_time'),
				unit_id = request.POST.get('unit_id'),
				)
			session.save()
			return http.HttpResponse('added')
	else:
		raise http.Http404