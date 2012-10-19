# Create your views here.
from django import http
from django.utils import simplejson as json
from tutablr_app.models import SessionTime, Enrolled, ClassTime, UnavailableTime, Booking, UOS, UnitDetails
from tutablr_app.forms import addBookingForm
from django.shortcuts import render_to_response
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import time, datetime
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

@login_required
def calendar_view(request, id):
	u = UnitDetails.objects.filter(user_id = id, is_tutorable = True)
	if len(u) == 0:
		return render(request, "non_tutor_calendar.html")
	else:
		if request.method == 'POST':
			form = addBookingForm(request.POST, tutor_id=id)
			if form.is_valid():
				print "valid!"
		else:
			form = addBookingForm(tutor_id=id)
		return render(request, "user_calendar.html", { 'form': form })
	#return render(request, "user_calendar.html")


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
            'selectable' : True,
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
            'selectable' : True,
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
            'selectable' : True,
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
            'selectable' : True,
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
            'selectable' : True,
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
                'id'  :  classtime.id,
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
            
def user_calendar(request, id):
        user_id = request.user.id
        enrolls = Enrolled.objects.filter (user_id=id) # get all the enrolled class for the student
        tutor_sessions = SessionTime.objects.filter (tutor_id=id) # get all the session time for the tutor
        student_sessions = SessionTime.objects.filter (student_id=id) # get all the session time for the tutee/student
        unavailable_times = UnavailableTime.objects.filter(user_id=id) # get all the unavailable times for the student
        tutor_bookings = Booking.objects.filter(tutor_id=id, is_rejected=False, is_confirmed=False)
        student_bookings = Booking.objects.filter(student_id=id, is_rejected=False, is_confirmed = False)
        calendar_list = [] # list for calender inputs
        #pending bookings-------------------------------------------------------------------
        for booking in tutor_bookings:
            if booking.student_id.id == user_id:
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
            else:
                booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
                booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
                calendar_list.append({
                'id'  :  booking.id,
                'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
                'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
                'title' : 'Unavailable',
                'allDay' : False,
                'backgroundColor' :  'red',
                'borderColor' : 'red',
                'editable' : False,
                'type' : 'tutor_booking'
                })
        for booking in student_bookings:
            if booking.tutor_id.id == user_id:
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
            else:
                booking_start = booking.start_time.astimezone(timezone.get_default_timezone())
                booking_finish = booking.finish_time.astimezone(timezone.get_default_timezone())
                calendar_list.append({
                'id'  :  booking.id,
                'start'  :  booking_start.strftime('%Y-%m-%d %H:%M:%S'),
                'end'  :  booking_finish.strftime('%Y-%m-%d %H:%M:%S'),
                'title' : 'Unavailable',
                'allDay' : False,
                'backgroundColor' :  'red',
                'borderColor' : 'red',
                'editable' : False,
                'type' : 'tutor_booking'
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
            'backgroundColor' :  'red',
            'borderColor' : 'red',
            'editable' : False,
            'type' : 'unavailable'
            })
        # for tutor sessions---------------------------------------------------------------
        for session in tutor_sessions:
            if session.student_id.id == user_id:
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
            else:
                session_start = session.start_time.astimezone(timezone.get_default_timezone())
                session_finish = session.finish_time.astimezone(timezone.get_default_timezone())
                calendar_list.append({
                'id'  :  session.id,
                'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
                'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
                'title' : 'Unavailable',
                'allDay' : False,
                'backgroundColor' :  'red',
                'borderColor' : 'red',
                'editable' : False,
                'type' : 'student_session'
                })
        # end of tutor sessions---------------------------------------------------------------  
        # for student sessions---------------------------------------------------------------
        for session in student_sessions:
            if session.student_id.id == user_id:
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
            else:
                session_start = session.start_time.astimezone(timezone.get_default_timezone())
                session_finish = session.finish_time.astimezone(timezone.get_default_timezone())

                calendar_list.append({
                'id'  :  session.id,
                'start'  :  session_start.strftime('%Y-%m-%d %H:%M:%S'),
                'end'  :  session_finish.strftime('%Y-%m-%d %H:%M:%S'),
                'title' : 'Unavailable',
                'allDay' : False,
                'backgroundColor' :  'red',
                'borderColor' : 'red',
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
                'backgroundColor' :  'red',
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

		#POST requests for the following three methods must have an id corresponding to the event id and a type corresponding to the event type
##id, type
def delete_booking(request, tutor_id):
	print("HEERHRHERHEHRERHRHE")
	if request.method == 'POST': 
		id = request.POST.get('edit_event_id')
		user_id = request.user.id
		booking = Booking.objects.get(pk=id)
		if booking.student_id.id == request.user.id:
			booking.delete()
			return redirect('/calendar/user/' + tutor_id + '/')
		else:
			raise http.Http404
	else:
		raise http.Http404

#POST requests here must also have a description, start_time, and finish_time
##id, type, description, start_time, finish_time, is_rejected, is_confirmed, 
def update(request):
		if request.method == 'POST':
			id = request.POST.get('edit_event_id')
			unavailable = UnavailableTime.objects.get(pk=id)
			user = unavailable.user_id
			print "hello"
			print user.id
			if user.id== request.user.id:
				start= request.POST.get('edit_start_date') + " " + request.POST.get('edit_start')
				start= time.strptime(start, "%d/%m/%Y %H:%M")
				start_datetime= datetime.datetime(*start[:6])
				end=  request.POST.get('edit_start_date') + " "+ request.POST.get('edit_end')
				end= time.strptime(end, "%d/%m/%Y %H:%M")
				end_datetime= datetime.datetime(*end[:6])
				unavailable.description = request.POST.get('edit_title')
				unavailable.start_time = start_datetime
				unavailable.finish_time = end_datetime
				print "hello"
				unavailable.save()
				return redirect('/calendar')
			else:
				raise http.Http404

		else:
			return redirect('/calendaKKr')
			
#POST requests here must also have a description, start_time, and finish_time
##id, type, description, start_time, finish_time, is_rejected, is_confirmed, 
def update_booking(request, other_id):
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
				booking.save()
				return redirect('/calendar/user/' + other_id + '/')
			else:
				raise http.Http404

		else:
			return redirect('/calendaKKr')

#POST requests here must also have a description, start_time, and finish_time
##type, tutor_id, student_id, description, start_time, finish_time, unit_id 
#http://api.jquery.com/jQuery.post/

# <script>
  # /* attach a submit handler to the form */
  # $("#searchForm").submit(function(event) {

    # /* stop form from submitting normally */
    # event.preventDefault(); 
        
    # /* get some values from elements on the page: */
    # var $form = $( this ),
        # start_date = $form.find( 'input[name="add_start_date"]' ).val(),
        # end_date = $form.find( 'input[name="add_end_date"]' ).val(),
        # type = $form.find( 'input[name="radio"]' ).val(),
        # start_time = $form.find( 'input[name="add_start"]' ).val(),
        # end_time = $form.find( 'input[name="add_end"]' ).val(),
        # description = $form.find( 'input[name=name="add_title"]' ).val(),
        # unit_id = $form.find( 'input[name=name="name="add_uos""]' ).val(),
        # url = $form.attr( 'action' );

    # /* Send the data using post and put the results in a div */
    # $.post( url, { 'start_time': start_date + ' ' + start_time, 'end_time': end_date + ' ' + end_time, 'type' : type, 'description' : description, 'unit_id' : unit_id},
      # function( data ) {
          # var content = $( data ).find( '#content' );
          # $( "#result" ).empty().append( content );
      # }
    # );
  # });
# </script>
    

def add_unavailable(request):
    
    if request.method == 'POST': 
        
        # if request.POST.get('type') == 'tutor_booking':
        # booking = Booking(tutor_id = user_id, 
        # student_id = request.POST.get('student_id'), 
        # description = request.POST.get('description'),
        # start_time = request.POST.get('start_time'),
        # finish_time = request.POST.get('finish_time'),
        # unit_id = request.POST.get('unit_id'),
        # is_rejected = False,
        # is_confirmed = False
        # )
        # booking.save()
        # return http.HttpResponse('added')
            start=  request.POST.get('add_start_date') + " " + request.POST.get('add_start')
            start= time.strptime(start, "%d/%m/%Y %H:%M")
            start_datetime= datetime.datetime(*start[:6])
            end=  request.POST.get('add_start_date') + " "+ request.POST.get('add_end')
            end= time.strptime(end, "%d/%m/%Y %H:%M")
            end_datetime= datetime.datetime(*end[:6])
    
            unavailable = UnavailableTime(user_id = request.user, 
                description = request.POST.get('add_title'),
                start_time = start_datetime,
                finish_time = end_datetime)
            print "test"
            unavailable.save()
            return redirect('/calendar')

def add_booking(request, id):
	print("HITHERE")
	if request.method == 'POST':
		start=  request.POST.get('date') + " " + request.POST.get('start_time')
		start= time.strptime(start, "%d/%m/%Y %H:%M")
		start_datetime= datetime.datetime(*start[:6])
		end=  request.POST.get('date') + " " + request.POST.get('finish_time')
		end= time.strptime(end, "%d/%m/%Y %H:%M")
		end_datetime= datetime.datetime(*end[:6])
		unit_id = UOS.objects.filter(unit_id = request.POST.get('UoS'))[0]
		tutor_id = User.objects.filter(id=id)[0]
		booking = Booking(unit_id = unit_id,
			start_time = start_datetime,
			finish_time = end_datetime,
			tutor_id = tutor_id,
			student_id = request.user,
			description = request.POST.get('description')
		)
		booking.save()
		#return HttpResponse("1")
		return redirect('/calendar/user/' + id + '/')
	else:
		return redirect('/calendar/user/' + id + '/')

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
            #return HttpResponseRedirect(redirect_to)
        else:
            return HttpResponse("0")
           # return HttpResponse("Username and password do not match!")
            #return HttpResponse(form.errors)

