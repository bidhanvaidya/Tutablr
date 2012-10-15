# Create your views here.
from django import http
from django.utils import simplejson as json
from tutablr_app.models import SessionTime
from django.shortcuts import render_to_response
from django.utils import timezone
def calendar(request):
	#user = request.user
	sessions = SessionTime.objects.filter (tutor_id=request.user.id)
	print request.user.id
	session_list = []
	print "penis"
	for session in sessions:
		print session.description + "<----"
		session_start = session.start_time.astimezone(timezone.get_default_timezone())
		session_finish = session.finish_time.astimezone(timezone.get_default_timezone())

		session_list.append({
			'id'  :  session.id,
			'start'  :  session_start.strftime('%Y-%m- %d %H:%M:%S'),
			 'end'  :  session_finish.strftime('%Y-%m- %d %H:%M:%S'),
			 'title' : session.description,
			 'allDay' : False,
			 'backgroundColor' :  'blue'
			})
		if len(session_list) == 0:
			raise http.Http404
		else:
			return http.HttpResponse(json.dumps(session_list), content_type='application/json')
	#return render_to_response('calendar.html')
		#session_start
