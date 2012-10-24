# Create your views here.
from django import http
from django.utils import simplejson as json
from tutablr_app.models import SessionTime, Enrolled, ClassTime, UnavailableTime, Booking, UOS, UnitDetails
from tutablr_app.forms import *
from django.shortcuts import render_to_response
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import time, datetime
from postman.models import Message, STATUS_ACCEPTED
import tutablr
from django.template import RequestContext
from django.shortcuts import redirect, render
from django.contrib.auth.models import User


@login_required
def tutor_search(request):
 	if request.method == 'POST': 
  		user_id = request.user.id
  		uos = request.POST.get('UoS')
  		price_from = request.POST.get('price_from')
  		price_to = request.POST.get('price_to')
  		distance_in_kms = request.POST.get('distance')
  		grade_from = request.POST.get('grade_from')
  		students_only = request.POST.get('students_only')
 		rating_from = request.POST.get('rating_from')
  		if students_only:
   			#eligible_tutors = User.objects.filter(userprofile.is_student_until__gr=datetime.now())
			eligible_tutors = User.objects.all()
  		else:
   			eligible_tutors= User.objects.all()
		form = searchForm()
		
	else:
		form = searchForm()

	return render(request, "search.html", { 'form': form })

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
			if booking.session_id is None:
				session_id = 0;
			else:
				session_id=booking.session_id.id
			booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
			booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
			if(booking.creator_id == request.user):
				draggable = True
			calendar_list.append({
			'id'  :  booking.id,
			'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : booking.description,
			'allDay' : False,
			'textColor' : 'black',
			'backgroundColor' :  '#949eff',
			'borderColor' : '#ff282a',
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
			if booking.session_id is None:
				session_id = 0;
			else:
				session_id=booking.session_id.id
			if(booking.creator_id == request.user):
				draggable = True
			booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
			booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
			calendar_list.append({
			'id'  :  booking.id,
			'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
			'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
			'title' : booking.description,
			'allDay' : False,
			'textColor' : 'black',
			'backgroundColor' :  '#949eff',
			'borderColor' : '#ff282a',
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
			if len(bookings) > 0:
				for b in bookings:
					if b.is_rejected == False and b.is_confirmed == False:
						pending = True
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
			'backgroundColor' :  '#5e7eff',
			'selectable' : True,
			'draggable' : True,
			'editable' : True,
			'pending' : pending,
			'type' : 'tutor_session'
			})
        # end of tutor sessions---------------------------------------------------------------  
        # for student sessions---------------------------------------------------------------
        for session in student_sessions:
			bookings = Booking.objects.filter(session_id=session)
			pending = False
			if len(bookings) > 0:
				for b in bookings:
					if b.is_rejected == False and b.is_confirmed == False:
						pending = True
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
			'backgroundColor' :  '#fffd79',
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
			if booking.session_id is None:
				session_id = 0;
			else:
				session_id=booking.session_id.id
			if booking.student_id.id == user_id:
				booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
				booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
				draggable = False
				if(booking.creator_id == request.user):
					draggable = True
				
				calendar_list.append({
				'id'  :  booking.id,
				'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : booking.description,
				'allDay' : False,
				'backgroundColor' :  '#949eff',
				'borderColor' : '#ff282a',
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
			if booking.session_id is None:
				session_id = 0;
			else:
				print("here!")
				session_id=booking.session_id.id
				print(session_id)
			if booking.tutor_id.id == user_id:
				booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
				booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
				draggable = False
				if(booking.creator_id == request.user):
					draggable = True
				
				calendar_list.append({
				'id'  :  booking.id,
				'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
				'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
				'title' : booking.description,
				'allDay' : False,
				'textColor' : 'black',
				'backgroundColor' :  '#949eff',
				'borderColor' : '#ff282a',
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
			if len(bookings) > 0:
				for b in bookings:
					if b.is_rejected == False and b.is_confirmed == False:
						pending = True
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
				'backgroundColor' :  '#5e7eff',
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
			if len(bookings) > 0:
				for b in bookings:
					if b.is_rejected == False and b.is_confirmed == False:
						pending = True
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
				'backgroundColor' :  '#fffd79',
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
				'backgroundColor' :  '#ffc58a',
				'borderColor' : '#ffc58a',
				'editable' : False,
				'type' : 'class'
				})
			# #end of class times---------------------------------------------------------------------
		if len(calendar_list) == 0:
			raise http.Http404
		else:
			return http.HttpResponse(json.dumps(calendar_list), content_type='application/json')
			
#POST requests for the following three methods must have an id corresponding to the event id and a type corresponding to the event type
##id, type
def delete(request):
    if request.method == 'POST': 
				id = request.POST.get('edit_event_id')
				user_id = request.user.id
				unavailable = UnavailableTime.objects.get(pk=id)
				user = unavailable.user_id
				if user.id== request.user.id:
					unavailable.delete()
					return redirect('/calendar')
				else:
					raise http.Http404
        
    else:
        raise http.Http404


#POST requests here must also have a description, start_time, and finish_time
##id, type, description, start_time, finish_time, is_rejected, is_confirmed, 
def update(request):
	return redirect('/notpost')
	if request.method == 'POST':
		id = request.POST.get('edit_event_id')
		start= request.POST.get('edit_start_date') + " " + request.POST.get('edit_start')
		start= time.strptime(start, "%d/%m/%Y %H:%M")
		start_datetime= datetime.datetime(*start[:6])
		end=  request.POST.get('edit_start_date') + " "+ request.POST.get('edit_end')
		end= time.strptime(end, "%d/%m/%Y %H:%M")
		end_datetime= datetime.datetime(*end[:6])
		if request.POST.get('type') == 'student_session':
				tutor_id= SessionTime.objects.get(pk=id).tutor_id
				unit_id= SessionTime.objects.get(pk=id).unit_id
				booking = Booking(unit_id = unit_id,
				start_time = start_datetime,
				finish_time = end_datetime,
				tutor_id = tutor_id,
				student_id = request.user,
				description = request.POST.get('edit_title')
				)
				booking.save()
				return redirect('/calendar')
		elif request.POST.get('type') == 'student_booking':
				booking = Booking.objects.get(pk=id)
				booking.description = request.POST.get('edit_title')
				booking.start_time = start_datetime
				booking.finish_time = end_datetime
				booking.save()
				return redirect('/calendar')
		elif request.POST.get('type') == 'unavailable':
			unavailable = UnavailableTime.objects.get(pk=id)
			user = unavailable.user_id
			if user.id== request.user.id:	
				print user.id
				unavailable.description = request.POST.get('edit_title')
				unavailable.start_time = start_datetime
				unavailable.finish_time = end_datetime
				print "hello"
				unavailable.save()
				return redirect('/calendar')
			else:
				return redirect('/wronguser')
		else:
			return redirect('/notpost')

#-------------------EVENT DROP----------------------------------
def drop_event(request, cal_id):
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
		elif eventType == "unavailable":
			unavailable = UnavailableTime.objects.filter(pk = event_id)[0]
			unavailable.start_time = unavailable.start_time + datetime.timedelta(days=int(dayDelta), minutes=int(minuteDelta))
			unavailable.finish_time = unavailable.finish_time + datetime.timedelta(days=int(dayDelta), minutes=int(minuteDelta))
			unavailable.save()
		#print(id)
		if cal_id == str(0):
			return redirect('/calendar/user/' + str(request.user.id) + '/')
		else:
			return redirect('/calendar/user/' + cal_id + '/')
			
#--------------------UNAVAILABLE TIMES--------------------------
def add_unavailable(request):
    if request.method == 'POST': 
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
		return redirect('/calendar/user/' + str(request.user.id) + '/')
		
def update_unavailable(request):
	if request.method == 'POST':
		id = request.POST.get('edit_unavailable_event_id')
		start= request.POST.get('edit_unavailable_date') + " " + request.POST.get('edit_unavailable_start')
		start= time.strptime(start, "%d/%m/%Y %H:%M")
		start_datetime= datetime.datetime(*start[:6])
		end=  request.POST.get('edit_unavailable_date') + " "+ request.POST.get('edit_unavailable_end')
		end= time.strptime(end, "%d/%m/%Y %H:%M")
		end_datetime= datetime.datetime(*end[:6])
		unavailable = UnavailableTime.objects.get(pk=id)
		user = unavailable.user_id
		if user.id== request.user.id:	
			print user.id
			unavailable.description = request.POST.get('edit_unavailable_title')
			unavailable.start_time = start_datetime
			unavailable.finish_time = end_datetime
			print "hello"
			unavailable.save()
			return redirect('/calendar/user/' + str(request.user.id) + '/')
		else:
			return redirect('/wronguser')
			
#POST requests for the following three methods must have an id corresponding to the event id and a type corresponding to the event type
##id, type
def delete_unavailable(request):
    if request.method == 'POST': 
		id = request.POST.get('edit_unavailable_event_id')
		user_id = request.user.id
		unavailable = UnavailableTime.objects.get(pk=id)
		user = unavailable.user_id
		if user.id== request.user.id:
			unavailable.delete()
			return redirect('/calendar/user/' + str(request.user.id) + '/')
		else:
			raise http.Http404
    else:
        raise http.Http404
#----------------END UNAVAILABLE TIMES------------
#----------------BOOKING--------------------------
#initial booking (with null session) MUST be made by the student
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
		if cal_id == str(0):
			return redirect('/calendar/user/' + str(request.user.id) + '/')
		else:
			return redirect('/calendar/user/' + cal_id + '/')
	else:
		return redirect('/calendar/user/' + cal_id + '/')
		
def update_booking(request, cal_id):
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
				booking.save()
				message.save()
				if cal_id == str(0):
					return redirect('/calendar/user/' + str(request.user.id) + '/')
				else:
					return redirect('/calendar/user/' + cal_id + '/')
			else:
				raise http.Http404

		else:
			return redirect('/calendaKKr')	
			
#initial booking MUST be made by the student
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
				if cal_id == str(0):
					return redirect('/calendar/user/' + str(request.user.id) + '/')
				else:
					return redirect('/calendar/user/' + cal_id + '/')
			else:
				raise http.Http404

		else:
			return redirect('/calendaKKr')

#initial booking MUST be made by the student
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
				booking.save()
				if cal_id == str(0):
					return redirect('/calendar/user/' + str(request.user.id) + '/')
				else:
					return redirect('/calendar/user/' + cal_id + '/')
			else:
				raise http.Http404

		else:
			return redirect('/calendaKKr')
			
def delete_booking(request, cal_id):
	if request.method == 'POST': 
		id = request.POST.get('edit_event_id')
		user_id = request.user.id
		booking = Booking.objects.get(pk=id)
		if booking.creator_id == request.user:
			booking.delete()
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
			
			if cal_id == str(0):
				return redirect('/calendar/user/' + str(request.user.id) + '/')
			else:
				return redirect('/calendar/user/' + cal_id + '/')
		else:
			print("herherherherh")
			raise http.Http404
	else:
		raise http.Http404
#-------------END BOOKINGS-----------------------
#-------------SESSIONS---------------------------
def update_session(request, cal_id):
		if request.method == 'POST':
			id = request.POST.get('edit_session_event_id')

			session = SessionTime.objects.get(pk=id)
			student = session.student_id
			tutor = session.tutor_id
			
			
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
				if cal_id == str(0):
					return redirect('/calendar/user/' + str(request.user.id) + '/')
				else:
					return redirect('/calendar/user/' + cal_id + '/')
			else:
				raise http.Http404

		else:
			return redirect('/calendaKKr')
			
def delete_session(request, cal_id):
	if request.method == 'POST': 
		id = request.POST.get('edit_session_event_id')
		user_id = request.user.id
		session = SessionTime.objects.get(pk=id)
		if session.student_id.id == request.user.id or session.tutor_id.id == request.user.id:
			session.delete()
			if cal_id == str(0):
				return redirect('/calendar/user/' + str(request.user.id) + '/')
			else:
				return redirect('/calendar/user/' + cal_id + '/')
		else:
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
    numberOfMessages = len(messages)
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

