# Create your views here.
from django import http
from django.utils import simplejson as json
from tutablr_app.models import SessionTime, Enrolled, ClassTime, UnavailableTime, Booking, UOS, UnitDetails, Location
from tutablr_app.forms import *
from django.shortcuts import render_to_response
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import time, datetime
from postman.models import Message, STATUS_ACCEPTED
import tutablr
from django.template import RequestContext
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from math import cos, sin, tan, atan2, sqrt

booking_locks = {}
session_locks = {}

#initialize the locks
#need to delete when the events are deleted and add when they are added
				
def lock(event_id, event_type):
	if event_type == "booking":
		booking_locks[str(event_id)] = True
	else:
		session_locks[str(event_id)] = True
		
def unlock(event_id, event_type):
	if event_type == "booking":
		booking_locks[str(event_id)] = False
	else:
		session_locks[str(event_id)] = False
@csrf_exempt
def get_lock(request):
    #lock status
    print "here"
    if request.method == "POST":
        event_id = request.POST.get('event_id')
        event_type = request.POST.get('event_type')
	print event_id
	print event_type
        if event_type == "booking":
            if booking_locks[str(event_id)] == False:
                lock(event_id, event_type)
		print "here1"
                return HttpResponse("1")
            else:
                return HttpResponse("0")
        else:
            if session_locks[str(event_id)] == False:
                    lock(event_id, event_type)
                    return HttpResponse("1")
            else:
                    return HttpResponse("0")

@csrf_exempt
def unlock_request(request):
	if request.method == "POST":
		event_id = request.POST.get('event_id')
		event_type = request.POST.get('event_type')
		unlock(event_id, event_type)
		return HttpResponse("1")
		
def radians(x):
        return x*3.14159/180.0

#0 is latitude, 1 is longitude
def haversine(p1, p2):
        R = 6371; #radians of earth in km
        print p2
        print p1
        dLat  = radians(p2[0] - p1[0])
        dLong = radians(p2[1] - p1[1])

        a = sin(dLat/2) * sin(dLat/2) + cos(radians(p1[0])) * cos(radians(p2[0])) * sin(dLong/2) * sin(dLong/2)
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        d = R * c
        return d

class eligibleTutorResult:
	def __init__(self, id, username, price, latitude, longitude, distance_in_kms, rating, timetable_url, profile_url):
		self.id=id
		self.username=username
		self.price=price
		self.latitude=latitude
		self.longitude=longitude
		self.distance_in_kms=distance_in_kms
		self.rating=rating
		self.timetable_url=timetable_url
		self.profile_url=profile_url
	
@login_required
def tutor_search(request):
	eligible_tutors = []
	eligible_tutor_results = []
	if request.method == 'POST': 
			user_id = request.user.id
			unit = request.POST.get('UoS')
			price_from = request.POST.get('price_from')
			price_to = request.POST.get('price_to')
			distance_in_kms = request.POST.get('distance')

	#grade_from = request.POST.get('grade_from')
			students_only = request.POST.get('students_only')
			rating_from = request.POST.get('rating_from')
			print user_id
			print unit
			print price_from
			print price_to
			print distance_in_kms
			print students_only
			print rating_from
			
			if students_only is not None:
			#current student
					eligible_tutors = User.objects.filter(userprofile__is_student_until__gt=datetime.now()).exclude(id = request.user.id)
			else:
			#all possible tutors
					eligible_tutors = User.objects.exclude(id = request.user.id)
			#between prices & for UoS
			eligible_tutors = list(set(eligible_tutors).intersection(set([e.user_id for e in UnitDetails.objects.filter(unit_id__unit_id = unit, price__gte=price_from, price__lte=price_to, is_tutorable=True)])))  
			#rating
			if int(rating_from) > 0:
					for t in eligible_tutors:
							ratings = [r.rating for r in Review.objects.filter(tutor_id__id = t.id)]
							if len(ratings) > 0:
									avg_rating = float(sum(ratings))/float(len(ratings))
									if avg_rating <= int(rating_from):
											eligible_tutors.remove(t)
							else:
											eligible_tutors.remove(t)
			#distance 
			if int(distance_in_kms) != 1000:
					user_location = [[l.latitude, l.longitude] for l in Location.objects.filter(user_id__id=request.user.id)]
					print len(user_location)
					if len(user_location) != 0:
							for t in eligible_tutors:
									found = False
									tutor_location = [[l.latitude, l.longitude] for l in TutoringLocation.objects.filter(user_id__id=t.id)]
									if len(tutor_location) == 0:
										eligible_tutors.remove(t)
									else:
										for l in tutor_location:
											if haversine(user_location, tutor_location[0]) < distance_in_kms:
												found = True
												break
										if not found:
											eligible_tutors.remove(t)	
																							
			for t in eligible_tutors:
				id = t.id
				username = t.username
				locations = [[l.latitude, l.longitude] for l in TutoringLocation.objects.filter(user_id__id=id)]
				avg_rating = 0
				user_location = [[l.latitude, l.longitude] for l in Location.objects.filter(user_id__id=request.user.id)]
				if len(locations) != 0 and len(user_location) != 0:
					distance_in_kms = 1000000
					latitude = 0
					longitude = 0
					for l in locations:
						if haversine(user_location[0], l) < distance_in_kms:
							distance_in_kms = haversine(user_location[0], l) 
							latitude = l[0]
							longitude = l[1]
				else:
					latitude = 0
					longitude=0
					distance_in_kms = 0
				ratings = [r.rating for r in Review.objects.filter(tutor_id__id = id)]
				if len(ratings) > 0:
						avg_rating = float(sum(ratings))/float(len(ratings))
				else:
					avg_rating = 0
				unit_details = UnitDetails.objects.filter(user_id__id = id, unit_id__unit_id = unit)
				price = unit_details[0].price
				profile_url = "/profiles/" + username + "/"
				timetable_url = "/calendar/user/" + str(id) + "/"
				eligible_tutor_results.append(eligibleTutorResult(id=id, 
					username=username, 
					price=price, 
					latitude="{0:.2f}".format(latitude), 
					longitude="{0:.2f}".format(longitude), 
					distance_in_kms="{0:.2f}".format(distance_in_kms), 
					rating="{0:.1f}".format(avg_rating), 
					timetable_url=timetable_url, 
					profile_url=profile_url))
				
			form = searchForm(user_id =request.user.id)
	else:
			form = searchForm(user_id = request.user.id)

	return render(request, "search.html", { 'form': form , 'eligible_tutor_results' : eligible_tutor_results})

@login_required
def calendar_user(request):
	return redirect('/calendar/user/' + str(request.user.id) + '/')

@login_required
def calendar_view(request, cal_id):
	if str(request.user.id) == str(cal_id):
		return render(request, "calendar.html")
	u = UnitDetails.objects.filter(user_id = cal_id, is_tutorable = True)
	if len(u) == 0:
		return render(request, "non_tutor_calendar.html")
	else:
		if request.method == 'POST':
			form = addBookingForm(request.POST, tutor_id=cal_id)
			if form.is_valid():
				print "valid!"
		else:
			form = addBookingForm(tutor_id=cal_id)
		return render(request, "user_calendar.html", { 'form': form })


@login_required
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
			draggable = False
			border_color = '#949eff'
			
			if booking.session_id is None:
				session_id = 0;
			else:
				session_id=booking.session_id.id
				border_color = '#ff282a'

			booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
			booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
			if booking.creator_id == request.user:
				draggable = True
			#else:
			#	border_color = '#ff282a'
			calendar_list.append({
			'id'  :  booking.id,
			'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : booking.description,
			'allDay' : False,
			'textColor' : 'black',
			'backgroundColor' :  '#949eff',
			'borderColor' : border_color,
			'draggable' : draggable,
			'selectable' : True,
			'editable' : True,
			'type' : 'tutor_booking',
			'session_id' : session_id,
			'creator_id' : booking.creator_id.id,
			'creator' : booking.creator_id.username,
            })
        for booking in student_bookings:
			draggable = False
			border_color = '#fffd79'

			if booking.session_id is None:
				session_id = 0;
			else:
				session_id=booking.session_id.id
				border_color =  '#ff282a'
			
			if booking.creator_id == request.user:
				draggable = True
			#else:
			#	border_color =  '#ff282a'
			booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
			booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
			calendar_list.append({
			'id'  :  booking.id,
			'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : booking.description,
			'allDay' : False,
			'textColor' : 'black',
			'backgroundColor' :  '#fffd79',
			'borderColor' : border_color,
			'draggable' : draggable,
			'selectable' : True,
			'editable' : True,
            		'type' : 'student_booking',
			'session_id' : session_id,
			'creator_id' : booking.creator_id.id,
			'creator' : booking.creator_id.username
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
			'textColor' : 'black',
            'backgroundColor' :  '#a2ff80',
			'draggable' : True,
            'selectable' : True,
            'editable' : True,
            'type' : 'unavailable'
            })
        # for tutor sessions---------------------------------------------------------------
        for session in tutor_sessions:
			bookings = Booking.objects.filter(session_id=session)
			pending = False
			border_color =  '#5e7eff'

			if len(bookings) > 0:
				for b in bookings:
					if b.is_rejected == False and b.is_confirmed == False:
						pending = True
						border_color = '#ff282a'
						break
			
						
			session_start = session.start_time.astimezone(timezone.get_default_timezone())
			session_finish = session.finish_time.astimezone(timezone.get_default_timezone())
			calendar_list.append({
			'id'  :  session.id,
			'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : session.description,
			'allDay' : False,
			'textColor' : 'white',
			'backgroundColor' :  '#1c04e0',
			'borderColor' : border_color,
			'selectable' : True,
			'draggable' : True,
			'editable' : True,
			'pending' : pending,
			'type' : 'tutor_session'
			})
        # end of tutor sessions---------------------------------------------------------------  
        # for student sessions---------------------------------------------------------------
        for session in student_sessions:
			border_color = '#e9863f'
			bookings = Booking.objects.filter(session_id=session)
			pending = False
			if len(bookings) > 0:
				for b in bookings:
					if b.is_rejected == False and b.is_confirmed == False:
						pending = True
						border_color = '#ff282a'
						break
			session_start = session.start_time.astimezone(timezone.get_default_timezone())
			session_finish = session.finish_time.astimezone(timezone.get_default_timezone())
			calendar_list.append({
			'id'  :  session.id,
			'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : session.description,
			'allDay' : False,
			'textColor' : 'black',
			'backgroundColor' :  '#e9863f',
			'borderColor' : border_color,
			'selectable' : True,
			'draggable' : True,
			'editable' : True,
			'pending' : pending,
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
                'id'  :  classtime.id,
                'start'  :  classtime_start.strftime('%Y-%m-%d %H:%M:%S'),
                'end'  :  classtime_finish.strftime('%Y-%m-%d %H:%M:%S'),
                'title' : classtime.description, #Enrolled.objects.get(id = enrolled.id).unit_id ,
                'allDay' : False,
				'textColor' : 'black',
                'backgroundColor' :  '#ffc58a',
                'editable' : False,
				'draggable' : False,
                'type' : 'class'
                })
            # #end of class times---------------------------------------------------------------------
        if len(calendar_list) == 0:
            raise http.Http404
        else:
            return http.HttpResponse(json.dumps(calendar_list), content_type='application/json')
            
def user_calendar(request, cal_id):
		user_id = request.user.id
		enrolls = Enrolled.objects.filter (user_id=cal_id) # get all the enrolled class for the student
		tutor_sessions = SessionTime.objects.filter (tutor_id=cal_id) # get all the session time for the tutor
		student_sessions = SessionTime.objects.filter (student_id=cal_id) # get all the session time for the tutee/student
		unavailable_times = UnavailableTime.objects.filter(user_id=cal_id) # get all the unavailable times for the student
		tutor_bookings = Booking.objects.filter(tutor_id=cal_id, is_rejected=False, is_confirmed=False)
		student_bookings = Booking.objects.filter(student_id=cal_id, is_rejected=False, is_confirmed = False)
		calendar_list = [] # list for calender inputs
		#pending bookings-------------------------------------------------------------------
		for booking in tutor_bookings:
			border_color = '#fffd79'

			if booking.session_id is None:
				session_id = 0;
			else:
				session_id=booking.session_id.id
				border_color =  '#ff282a'

			if booking.student_id.id == user_id:
				booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
				booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
				draggable = False
				border_color =  '#949eff'
				if booking.creator_id == request.user:
					draggable = True
				#else:
				#	border_color =  '#ff282a'
				if booking.session_id is not None:
					border_color =  '#ff282a'
				calendar_list.append({
				'id'  :  booking.id,
				'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : booking.description,
				'allDay' : False,
				'backgroundColor' :  '#fffd79',
				'borderColor' : border_color,
				'editable' : True,
				'type' : 'tutor_booking',
				'draggable' : draggable,
				'session_id' : session_id,
				'creator_id' : booking.creator_id.id,
				'creator' : booking.creator_id.username
				})
			else:
				booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
				booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
				calendar_list.append({
				'id'  :  booking.id,
				'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : 'Unavailable',
				'allDay' : False,
				'backgroundColor' :  '#ff282a',
				'borderColor' : '#ff282a',
				'editable' : False,
				'type' : 'tutor_booking',
				'session_id' : session_id,
				'creator_id' : booking.creator_id.id,
				'creator' : booking.creator_id.username,
				})
		for booking in student_bookings:
			border_color = '#949eff'

			if booking.session_id is None:
				session_id = 0;
			else:
				session_id=booking.session_id.id
				border_color =  '#ff282a'
			if booking.tutor_id.id == user_id:
				booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
				booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
				draggable = False
				border_color = '#fffd79'
				if(booking.creator_id == request.user):
					draggable = True
				#else:
				#	border_color =  '#ff282a'

				calendar_list.append({
				'id'  :  booking.id,
				'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : booking.description,
				'allDay' : False,
				'textColor' : 'black',
				'backgroundColor' :  '#949eff',
				'borderColor' : border_color,
				'editable' : True,
				'draggable' : draggable,
				'type' : 'student_booking',
				'session_id' : session_id,
				'creator_id' : booking.creator_id.id
				})
			else:
				booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
				booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
				calendar_list.append({
				'id'  :  booking.id,
				'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : 'Unavailable',
				'allDay' : False,
				'backgroundColor' :  '#ff282a',
				'borderColor' : '#ff282a',
				'editable' : False,
				'type' : 'tutor_booking',
				'session_id' : session_id,
				'creator_id' : booking.creator_id.id
				})
		# unavailable times---------------------------------------------------------------
		for ut in unavailable_times:
			session_start = ut.start_time.astimezone(timezone.get_default_timezone())
			session_finish = ut.finish_time.astimezone(timezone.get_default_timezone())
			calendar_list.append({
			'id'  :  ut.id,
			'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : 'Unavailable',
			'allDay' : False,
			'backgroundColor' :  '#ff282a',
			'borderColor' : '#ff282a',
			'editable' : False,
			'type' : 'unavailable'
			})
		# for tutor sessions---------------------------------------------------------------
		for session in tutor_sessions:
			bookings = Booking.objects.filter(session_id=session)
			pending = False
			border_color = '#e9863f'

			if len(bookings) > 0:
				for b in bookings:
					if b.is_rejected == False and b.is_confirmed == False:
						pending = True
						border_color = '#ff282a'
						break
			if session.student_id.id == user_id or session.tutor_id.id == user_id:
				session_start = session.start_time.astimezone(timezone.get_default_timezone())
				session_finish = session.finish_time.astimezone(timezone.get_default_timezone())
				calendar_list.append({
				'id'  :  session.id,
				'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : session.description,
				'allDay' : False,
				'textColor' : 'white',
				'backgroundColor' :  '#e9863f',
				'borderColor' : border_color,
				'draggable' : True,
				'editable' : True,
				'pending' : pending,
				'type' : 'tutor_session'
				})
			else:
				session_start = session.start_time.astimezone(timezone.get_default_timezone())
				session_finish = session.finish_time.astimezone(timezone.get_default_timezone())
				calendar_list.append({
				'id'  :  session.id,
				'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : 'Unavailable',
				'allDay' : False,
				'backgroundColor' :  '#ff282a',
				'borderColor' : '#ff282a',
				'editable' : False,
				'type' : 'student_session'
				})
		# end of tutor sessions---------------------------------------------------------------  
		# for student sessions---------------------------------------------------------------
		for session in student_sessions:
			bookings = Booking.objects.filter(session_id=session)
			pending = False
			border_color = '#1c04e0'

			if len(bookings) > 0:
				for b in bookings:
					if b.is_rejected == False and b.is_confirmed == False:
						pending = True
						border_color = '#5e7eff'
						break
			if session.student_id.id == user_id or session.tutor_id.id == user_id:
				session_start = session.start_time.astimezone(timezone.get_default_timezone())
				session_finish = session.finish_time.astimezone(timezone.get_default_timezone())
				calendar_list.append({
				'id'  :  session.id,
				'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : session.description,
				'allDay' : False,
				'textColor' : 'black',
				'backgroundColor' :  '#1c04e0',
				'borderColor' : border_color,
				'draggable' : True,
				'editable' : True,
				'pending' : pending,
				'type' : 'student_session'
				})
			else:
				session_start = session.start_time.astimezone(timezone.get_default_timezone())
				session_finish = session.finish_time.astimezone(timezone.get_default_timezone())

				calendar_list.append({
				'id'  :  session.id,
				'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : 'Unavailable',
				'allDay' : False,
				'backgroundColor' :  '#ff282a',
				'borderColor' : '#ff282a',
				'editable' : False,
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
				'id'  :  classtime.id,
				'start'  :  classtime_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  classtime_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : 'Unavailable',
				'allDay' : False,
				'backgroundColor' :  '#ff282a',
				'borderColor' : '#ff282a',
				'editable' : False,
				'type' : 'class'
				})
			# #end of class times---------------------------------------------------------------------
		if len(calendar_list) == 0:
			raise http.Http404
		else:
			return http.HttpResponse(json.dumps(calendar_list), content_type='application/json')
			

#-------------------EVENT DROP----------------------------------
@csrf_exempt
def drop_event(request, cal_id):
	print request.user.id
	if request.method == 'POST':
		dayDelta = request.POST.get('dayDelta')
		minuteDelta = request.POST.get('minuteDelta')
		eventType = request.POST.get('eventType')
		event_id = request.POST.get('drop_event_id')
		if eventType == 'student_session' or eventType == 'tutor_session':
			session = SessionTime.objects.get(pk=event_id)
			booking = Booking(start_time = session.start_time + datetime.timedelta(days=int(dayDelta), minutes=int(minuteDelta)),
					finish_time = session.finish_time + datetime.timedelta(days=int(dayDelta), minutes=int(minuteDelta)),
					creator_id = request.user,
					session_id = session,
					description = session.description,
					tutor_id = session.tutor_id,
					student_id = session.student_id,
					unit_id = session.unit_id)
			print "creator id" + str(request.user.id)
			now= datetime.datetime.now()
			admin= User.objects.all()[0]
			if request.POST.get('type') == 'student_session':
				message= Message(subject=" Change for existing session", 
					body="Your student  "+ request.user.username +" has requested for a change for "+session.unit_id.unit_id +" You will need to confirmed it", 
					sender=admin, 
					recipient=session.tutor_id, 
					moderation_status=STATUS_ACCEPTED, 
					moderation_date=now)
			else:
				message= Message(subject=" Change for existing session", 
                        body="Your tutor  "+ request.user.username +" has requested for a change for "+session.unit_id.unit_id +" You will need to confirmed it", 
                        sender=admin, 
                        recipient=session.student_id,
                        moderation_status=STATUS_ACCEPTED, 
                        moderation_date=now)
			message.save()
			booking.save()
			#add to locks
			booking_locks[str(booking.id)] = False
			#unlock the event
			unlock(event_id, eventType)
		elif eventType == 'student_booking' or eventType == 'tutor_booking':
			booking = Booking.objects.filter(pk=event_id)[0]
			booking.start_time = booking.start_time + datetime.timedelta(days=int(dayDelta), minutes=int(minuteDelta))
			booking.finish_time = booking.finish_time + datetime.timedelta(days=int(dayDelta), minutes=int(minuteDelta))
			booking.save()
			now= datetime.datetime.now()
			admin= User.objects.all()[0]
			if booking.student_id == request.user :
				message= Message(subject="Booking Updated", 
						body=" A booking for " +  booking.unit_id.unit_name+"has been changed by " + booking.student_id.username, 
						sender=admin, 
						recipient=booking.tutor_id, 
						moderation_status=STATUS_ACCEPTED, 
						moderation_date=now)
			else:
				message= Message(subject="Booking Updated", 
						body="Your booking for " +  booking.unit_id.unit_name+"has been changed by " + booking.tutor_id.username + "You will need to confirm it create a session", 
						sender=admin, 
						recipient=booking.tutor_id, 
						moderation_status=STATUS_ACCEPTED, 
						moderation_date=now)
			message.save()
			#unlock the event
			unlock(event_id, eventType)
		elif eventType == "unavailable":
			unavailable = UnavailableTime.objects.filter(pk = event_id)[0]
			unavailable.start_time = unavailable.start_time + datetime.timedelta(days=int(dayDelta), minutes=int(minuteDelta))
			unavailable.finish_time = unavailable.finish_time + datetime.timedelta(days=int(dayDelta), minutes=int(minuteDelta))
			unavailable.save()
		return HttpResponse("1")

			
#--------------------UNAVAILABLE TIMES--------------------------
@csrf_exempt
def add_unavailable(request):
    if request.method == 'POST': 
		print  request.POST.get('add_unavailable_date')
		start=  request.POST.get('add_unavailable_date') + " " + request.POST.get('add_unavailable_start_time')
		start= time.strptime(start, "%d/%m/%Y %H:%M")
		start_datetime= datetime.datetime(*start[:6])
		end=  request.POST.get('add_unavailable_date') + " "+ request.POST.get('add_unavailable_finish_time')
		end= time.strptime(end, "%d/%m/%Y %H:%M")
		end_datetime= datetime.datetime(*end[:6])
		unavailable = UnavailableTime(user_id = request.user, 
			description = request.POST.get('add_unavailable_title'),
			start_time = start_datetime,
			finish_time = end_datetime)
		print "test"
		unavailable.save()
		#return redirect('/calendar/user/' + str(request.user.id) + '/')
		return HttpResponse("1")

@csrf_exempt
def update_unavailable(request):
	print "hits"
	print request.method
	if request.method == 'POST':
		print request.POST
		id = request.POST.get('edit_unavailable_event_id')
		start= request.POST.get('edit_unavailable_date') + " " + request.POST.get('edit_unavailable_start')
		print "STEP 2"
		start= time.strptime(start, "%d/%m/%Y %H:%M")
		start_datetime= datetime.datetime(*start[:6])
		end=  request.POST.get('edit_unavailable_date') + " "+ request.POST.get('edit_unavailable_end')
		end= time.strptime(end, "%d/%m/%Y %H:%M")
		end_datetime= datetime.datetime(*end[:6])
		unavailable = UnavailableTime.objects.get(pk=id)
		user = unavailable.user_id
		print "STEP 2"
		if user.id== request.user.id:	
			print user.id
			unavailable.description = request.POST.get('edit_unavailable_title')
			unavailable.start_time = start_datetime
			unavailable.finish_time = end_datetime
			print "hello"
			try:
				unavailable.save()
			except Exception,e: 
				print str(e)
			print "hello CATCAT"
			#return redirect('/calendar/user/' + str(request.user.id) + '/')
			return HttpResponse("1")
		else:
			return HttpResponse("0")
			#return redirect('/wronguser')
			
#POST requests for the following three methods must have an id corresponding to the event id and a type corresponding to the event type
##id, type
@csrf_exempt
def delete_unavailable(request):
    if request.method == 'POST': 
		id = request.POST.get('edit_unavailable_event_id')
		user_id = request.user.id
		unavailable = UnavailableTime.objects.get(pk=id)
		user = unavailable.user_id
		if user.id== request.user.id:
			unavailable.delete()
			#return redirect('/calendar/user/' + str(request.user.id) + '/')
			return HttpResponse("1")
		else:
			#raise http.Http404
			return HttpResponse("0")
    else:
        #raise http.Http404
	return HttpResponse("0")
#----------------END UNAVAILABLE TIMES------------
#----------------BOOKING--------------------------
#initial booking (with null session) MUST be made by the student
@csrf_exempt
def add_booking(request, cal_id):
	if request.method == 'POST':
		start=  request.POST.get('date') + " " + request.POST.get('start_time')
		start= time.strptime(start, "%d/%m/%Y %H:%M")
		start_datetime= datetime.datetime(*start[:6])
		end=  request.POST.get('date') + " " + request.POST.get('finish_time')
		end= time.strptime(end, "%d/%m/%Y %H:%M")
		end_datetime= datetime.datetime(*end[:6])
		unit_id = UOS.objects.filter(unit_id = request.POST.get('UoS'))[0]
		#other_id = User.objects.filter(id=cal_id)[0]
		booking = Booking(unit_id = unit_id,
			start_time = start_datetime,
			finish_time = end_datetime,
			tutor_id = User.objects.filter(id=cal_id)[0],
			student_id = request.user,
			description = request.POST.get('description'),
			creator_id = request.user
		)
		now= datetime.datetime.now()
		admin= User.objects.all()[0]
		message= Message(subject="Booking Created", 
			body=" A booking for " +  booking.unit_id.unit_name+" has been created by " + booking.creator_id.username, 
			sender=admin, 
			recipient=booking.tutor_id, 
			moderation_status=STATUS_ACCEPTED, 
			moderation_date=now)
		message.save()
		message= Message(subject="Booking Created", 
			body=" You have created a booking for " +  booking.unit_id.unit_name+" with " + booking.tutor_id.username, 
			sender=admin, 
			recipient=booking.student_id, 
			moderation_status=STATUS_ACCEPTED, 
			moderation_date=now)
		message.save()
	
		booking.save()
		#add to booking_locks
		booking_locks[str(booking.id)] = False
		if cal_id == str(0):
			return redirect('/calendar/user/' + str(request.user.id) + '/')
		else:
			return redirect('/calendar/user/' + cal_id + '/')
	else:
		return redirect('/calendar/user/' + cal_id + '/')

@csrf_exempt	
def update_booking(request, cal_id):
		if request.method == 'POST':
			print request.POST
			id = request.POST.get('edit_event_id')
			booking = Booking.objects.get(pk=id)
			student = booking.student_id
			tutor = booking.tutor_id
			if student.id== request.user.id or tutor.id== request.user.id:
				start= request.POST.get('edit_start_date') + " " + request.POST.get('edit_start')
				start= time.strptime(start, "%d/%m/%Y %H:%M")
				start_datetime= datetime.datetime(*start[:6])
				end=  request.POST.get('edit_start_date') + " "+ request.POST.get('edit_end')
				end= time.strptime(end, "%d/%m/%Y %H:%M")
				end_datetime= datetime.datetime(*end[:6])
				booking.description = request.POST.get('edit_title')
				booking.start_time = start_datetime
				booking.finish_time = end_datetime
				now= datetime.datetime.now()
				admin= User.objects.all()[0]
				if booking.student_id == request.user :
					message= Message(subject="Booking Updated", 
							body=" A booking for " +  booking.unit_id.unit_name+"has been changed by " + booking.student_id.username, 
							sender=admin, 
							recipient=booking.tutor_id, 
							moderation_status=STATUS_ACCEPTED, 
							moderation_date=now)
				else:
					message= Message(subject="Booking Updated", 
							body="Your booking for " +  booking.unit_id.unit_name+"has been changed by " + booking.tutor_id.username + "You will need to confirm it create a session", 
							sender=admin, 
							recipient=booking.tutor_id, 
							moderation_status=STATUS_ACCEPTED, 
							moderation_date=now)

				booking.creator_id = request.user
				try:
					booking.save()
				except Exception,e: 
					print str(e)
				#booking.save()
				#release booking lock
				unlock(booking.id, "booking")
				message.save()
				if cal_id == str(0):
					return redirect('/calendar/user/' + str(request.user.id) + '/')
				else:
					return redirect('/calendar/user/' + cal_id + '/')
			else:
				unlock(booking.id, "booking")
				raise http.Http404

		else:
			return redirect('/calendaKKr')	
			
#initial booking MUST be made by the student
@csrf_exempt
def confirm_booking(request, cal_id):
	if request.method == 'POST':
		id = request.POST.get('edit_event_id')
		booking = Booking.objects.get(pk=id)
		student = booking.student_id
		tutor = booking.tutor_id
		old_session = booking.session_id

			
		if (student.id== request.user.id or tutor.id== request.user.id) and request.user.id != booking.creator_id.id:
			start= request.POST.get('edit_start_date') + " " + request.POST.get('edit_start')
			start= time.strptime(start, "%d/%m/%Y %H:%M")
			start_datetime= datetime.datetime(*start[:6])
			end=  request.POST.get('edit_start_date') + " "+ request.POST.get('edit_end')
			end= time.strptime(end, "%d/%m/%Y %H:%M")
			end_datetime= datetime.datetime(*end[:6])
			booking.description = request.POST.get('edit_title')
			booking.start_time = start_datetime
			booking.finish_time = end_datetime
			booking.is_confirmed = True

			if old_session != None:
				print old_session
				old_session.delete()
				
			session = SessionTime(unit_id = booking.unit_id,
						description = booking.description,
						start_time = booking.start_time,
						finish_time = booking.finish_time,
						tutor_id = booking.tutor_id,
						student_id = booking.student_id)
			session.save()
			#add to session locks
                	session_locks[str(session.id)] = False
			#############
                	now= datetime.datetime.now()
                	admin= User.objects.all()[0]
        		if booking.creator_id == booking.student_id:
        			message= Message(subject="Session Created", 
        				body="Your Booking has been accepted. Your tutoring session for " +  booking.unit_id.unit_name+"has been created with " + booking.tutor_id.username, 
        				sender=admin, 
        				recipient=booking.student_id, 
        				moderation_status=STATUS_ACCEPTED, 
        				moderation_date=now)
        			message.save()
        			message= Message(subject="Session Created", 
        				body="You have accepted a booking. Your tutoring session for " +  booking.unit_id.unit_name+"has been created with " + booking.student_id.username, 
        				sender=admin, 
        				recipient=booking.tutor_id, 
        				moderation_status=STATUS_ACCEPTED, 
        				moderation_date=now)
       				message.save()
       			else:
       				message= Message(subject="Session Created", 
        				body="Booking session has been approved by your tutor. Your tutoring session for " +  booking.unit_id.unit_name+"has been created with " + booking.tutor_id.username, 
        				sender=admin, 
        				recipient=booking.student_id, 
        				moderation_status=STATUS_ACCEPTED, 
        				moderation_date=now)
       				message.save()
       				message= Message(subject="Booking Rejected", 
        				body="Booking with the changes you made have been approved. Your Booking for "+ booking.unit_id.unit_name+" has been rejected by " + booking.tutor_id.username, 
        				sender=admin, 
        				recipient=booking.tutor_id, 
        				moderation_status=STATUS_ACCEPTED, 
  	     				moderation_date=now)
       				message.save()	
       			booking.save()
       			#unlock booking
       			unlock(booking.id, "booking")
                	################
       			if cal_id == str(0):
       				return redirect('/calendar/user/' + str(request.user.id) + '/')
       			else:
       				return redirect('/calendar/user/' + cal_id + '/')
       		else:
        		unlock(booking.id, "booking")
        		raise http.Http404

        else:
        	return redirect('/calendaKKr')

#initial booking MUST be made by the student
@csrf_exempt
def reject_booking(request, cal_id):
		if request.method == 'POST':
			id = request.POST.get('edit_event_id')
			booking = Booking.objects.get(pk=id)
			student = booking.student_id
			tutor = booking.tutor_id
			if student.id== request.user.id or tutor.id== request.user.id:
				start= request.POST.get('edit_start_date') + " " + request.POST.get('edit_start')
				start= time.strptime(start, "%d/%m/%Y %H:%M")
				start_datetime= datetime.datetime(*start[:6])
				end=  request.POST.get('edit_start_date') + " "+ request.POST.get('edit_end')
				end= time.strptime(end, "%d/%m/%Y %H:%M")
				end_datetime= datetime.datetime(*end[:6])
				booking.description = request.POST.get('edit_title')
				booking.start_time = start_datetime
				booking.finish_time = end_datetime
				booking.is_rejected = True
				now= datetime.datetime.now()
				admin= User.objects.all()[0]
				if booking.creator_id == booking.student_id:
					message= Message(subject="Booking Rejected", 
						body="You have rejected a booking by " +  booking.creator_id.username+ " for "+ booking.unit_id.unit_name, 
						sender=admin, 
						recipient=booking.tutor_id, 
						moderation_status=STATUS_ACCEPTED, 
						moderation_date=now)
					message.save()
					message= Message(subject="Booking Rejected", 
						body="Your Booking for "+ booking.unit_id.unit_name+" has been rejected by " + booking.tutor_id.username, 
						sender=admin, 
						recipient=booking.creator_id, 
						moderation_status=STATUS_ACCEPTED, 
						moderation_date=now)
					message.save()
				else:
					message= Message(subject="Booking Rejected", 
						body="You have rejected a booking by " +  booking.creator_id.username+ " for "+ booking.unit_id.unit_name, 
						sender=admin, 
						recipient=booking.student_id, 
						moderation_status=STATUS_ACCEPTED, 
						moderation_date=now)
					message.save()
					message= Message(subject="Booking Rejected", 
						body="Your Booking for "+ booking.unit_id.unit_name+" has been rejected by " + booking.tutor_id.username, 
						sender=admin, 
						recipient=booking.creator_id, 
						moderation_status=STATUS_ACCEPTED, 
						moderation_date=now)
					message.save()	
				#unlock booking
				booking.save()
				unlock(booking.id, "booking")
				if cal_id == str(0):
					return redirect('/calendar/user/' + str(request.user.id) + '/')
				else:
					return redirect('/calendar/user/' + cal_id + '/')
			else:
				unlock(booking.id, "booking")
				raise http.Http404

		else:
			return redirect('/calendaKKr')
@csrf_exempt		
def delete_booking(request, cal_id):
	if request.method == 'POST': 
		id = request.POST.get('edit_event_id')
		user_id = request.user.id
		booking = Booking.objects.get(pk=id)
		if booking.creator_id == request.user:
			now= datetime.datetime.now()
			admin= User.objects.all()[0]
			if booking.creator_id == booking.student_id:
				message= Message(subject="Booking Deleted", 
					body="A Booking of "+ booking.unit_id.unit_name + " has been deleted by " + booking.creator_id.username, 
					sender=admin, 
					recipient=booking.tutor_id, 
					moderation_status=STATUS_ACCEPTED, 
					moderation_date=now)
			else:
				message= Message(subject="Booking Deleted", 
					body="A Booking of "+ booking.unit_id.unit_name +" has been deleted by " + booking.creator_id.username, 
					sender=admin, 
					recipient=booking.student_id, 
					moderation_status=STATUS_ACCEPTED, 
					moderation_date=now)	
			message.save()
			#delete booking
			del booking_locks[str(booking.id)]
			booking.delete()
			if cal_id == str(0):
				return redirect('/calendar/user/' + str(request.user.id) + '/')
			else:
				return redirect('/calendar/user/' + cal_id + '/')
		else:
			unlock(booking.id, "booking")
			raise http.Http404
	else:
		raise http.Http404
#-------------END BOOKINGS-----------------------
#-------------SESSIONS---------------------------
@csrf_exempt
def update_session(request, cal_id):
		if request.method == 'POST':
			print request.POST
			try:
				print "hi"
			except Exception,e: 
				print str(e)
			id = request.POST.get('edit_session_event_id')
			session = SessionTime.objects.get(pk=id)
			student = session.student_id
			tutor = session.tutor_id
			print "BBB"
			if student.id== request.user.id or tutor.id== request.user.id:
				start= request.POST.get('edit_session_start_date') + " " + request.POST.get('edit_session_start')
				start= time.strptime(start, "%d/%m/%Y %H:%M")
				start_datetime= datetime.datetime(*start[:6])
				end=  request.POST.get('edit_session_start_date') + " "+ request.POST.get('edit_session_end')
				end= time.strptime(end, "%d/%m/%Y %H:%M")
				end_datetime= datetime.datetime(*end[:6])
				session_start_time=timezone.make_aware(session.start_time, timezone.get_default_timezone()) + datetime.timedelta(0,39600)
				calendar_start= timezone.make_aware(start_datetime, timezone.get_default_timezone())
				session_end_time= timezone.make_aware(session.finish_time, timezone.get_default_timezone()) + datetime.timedelta(0,39600)
				calendar_end= timezone.make_aware(end_datetime, timezone.get_default_timezone())
				print "AAA"
				if session_start_time == calendar_start and session_end_time == calendar_end:
					session.description = request.POST.get('edit_session_title')
					session.save()
					
				else:
					description = request.POST.get('edit_session_title')
					now= datetime.datetime.now()
					admin= User.objects.all()[0]
					if request.POST.get('type') == 'student_session':
						message= Message(subject=" Change for existing session", 
							body="Your student  "+ request.user.username +" has requested for a change for "+session.unit_id.unit_id +" You will need to confirmed it", 
							sender=admin, 
							recipient=session.tutor_id, 
							moderation_status=STATUS_ACCEPTED, 
							moderation_date=now)
					else:
						message= Message(subject=" Change for existing session", 
                                body="Your tutor  "+ request.user.username +" has requested for a change for "+session.unit_id.unit_id +" You will need to confirmed it", 
                                sender=admin, 
                                recipient=student, 
                                moderation_status=STATUS_ACCEPTED, 
                                moderation_date=now)
					print "HELO WORLD"
					print session
					booking = Booking(start_time = start_datetime, 
						finish_time = end_datetime,
						creator_id = request.user,
						session_id = session,
						description = description,
						tutor_id = tutor,
						student_id = student,
						unit_id = session.unit_id)
					message.save()
					booking.save()
					booking_locks[str(booking.id)] = False
					#add booking to locks
				#unlock session
				unlock(session.id, "session")
				if cal_id == str(0):
					return redirect('/calendar/user/' + str(request.user.id) + '/')
				else:
					return redirect('/calendar/user/' + cal_id + '/')
			else:
				unlock(session.id, "session")
				raise http.Http404
		else:
			return redirect('/calendaKKr')
@csrf_exempt		
def delete_session(request, cal_id):
	if request.method == 'POST': 
		id = request.POST.get('edit_session_event_id')
		user_id = request.user.id
		session = SessionTime.objects.get(pk=id)
		if session.student_id.id == request.user.id or session.tutor_id.id == request.user.id:
			del session_locks[str(session.id)]
			session.delete()
			if cal_id == str(0):
				return redirect('/calendar/user/' + str(request.user.id) + '/')
			else:
				return redirect('/calendar/user/' + cal_id + '/')
		else:
			unlock(session.id, "session")
			raise http.Http404
	else:
			raise http.Http404
#-----------------END SESSIONS-----------------------
			
			
	
def loginAjax(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username = request.POST['username'],password = request.POST['password'])
            if user is not None:
                login(request,user)
                redirect_to = '/'
            else:
                redirect_to = '/'
            return HttpResponse("1")
        else:
            return HttpResponse("0")

def contactFormAjax(request):
    if request.method == "POST":
        if request.is_ajax:
            name = request.POST.get("fullName")
            message = request.POST.get("message")
            email = request.POST.get("email")
            tempMessage = "Name: " +  name + "\n" + "Email: " + email + "\n" + "Message: " + message + "\n"
            senderUser =  User.objects.get(username="ContactForm")
            recieverUser = User.objects.get(username="admin")
            m = Message(subject="Contact Form Message!!", body=tempMessage,sender=senderUser,recipient=recieverUser,moderation_status='a')
            m.save()
            print request.POST
            return HttpResponse("1")
        else:
            print "NOT AJAX"
    return HttpResponse("0") 

@login_required
def dashboard(request):
    user_id = request.user.id
    #print tutablr.settings.STATIC_ROOT +" <------"
    arrayMessages = Message.objects.filter(recipient=user_id).exclude(read_at__isnull=False)
    messages = arrayMessages[:5]
    numberOfMessages = len(arrayMessages)
    extraRows = 5 - numberOfMessages
    if extraRows > 0:
        temp = "<tr><td height=\"18\"></td></tr>"*extraRows
        print temp + " <------------"
    else:
        temp = ""
    print  messages
    return render_to_response('dashboard.html',
                              {"messages":messages,
                                 "numberOfMessages":numberOfMessages,
                                 "extraRows":temp,
                              },
                              context_instance=RequestContext(request)
   )

@login_required
def location(request):
	return render_to_response("location.html",
		{},
		context_instance = RequestContext(request)
	)

@login_required
def locationEditPersonal(request):
	if request.method == "POST":
		loc = Location.objects.get(user_id=request.user)
		f = LocationForm(request.POST,instance=loc)
		f.save()
		#print (request.get.POST)
		return render_to_response("location_edit_personal.html",
			{"response":"Successfully changed location.",
			},
			context_instance = RequestContext(request)
		)
	else:
		try: #get location
			loc = Location.objects.get(user_id=request.user)
		except Location.DoesNotExist: # create location
			print "Making Location"
			loc = Location(preferred_suburb="Sydney",longitude=151.20699020000006 ,latitude=-33.8674869,user_id=request.user)
			loc.save()

		form = LocationForm(instance=loc)
		return render_to_response("location_edit_personal.html",
			{"form":form,
			},
			context_instance = RequestContext(request)
		)

@login_required
def locationAddTutoring(request):
	if request.method == "POST":
		print (request.get.POST)
	else:
		form = TutorLocationForm()
		return render_to_response("locationAdd.html",
			{"form":form,},
			context_instance = RequestContext(request)
		)
"""
@login_required
def locationSelector(request):
	if request.method == "POST":
		print (request.get.POST)
	else:
		if request.user
		form = LocationForm()
		return render_to_response("locationAdd.html",
			{"form":form,},
			context_instance = RequestContext(request)
		)
"""
