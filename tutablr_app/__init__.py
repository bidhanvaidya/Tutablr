from tutablr_app.models import Booking, SessionTime
from tutablr_app.views import *

#initialize the locks from the database

bookings = Booking.objects.all()
sessions = SessionTime.objects.all()
for b in bookings:
	booking_locks[str(b.id)] = False

	
for s in sessions:
	session_locks[str(s.id)] = False