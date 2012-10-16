from django.db import models
from django.contrib.auth.models import User
from tutablr.custom_fields import IntegerRangeField
from django.db.models import signals
from tutablr_app.signals import create_profile
from datetime import datetime
#signals.post_save.connect(create_profile, sender=User)

# Model to extend the contrib.auth user model
class UserProfile(models.Model):
	user = models.OneToOneField(User)
	#additional fields to the user model:
	is_student_until = models.DateField(default=datetime.now()) 
	home_phone = models.IntegerField(max_length = 10, default = 0)
	mobile_phone = models.IntegerField(max_length=11, default = 0)
	about_me = models.TextField(max_length=400, default = "")
	extra_details = models.TextField(max_length=400, default = "")
	is_approved = models.BooleanField(default=False)
	def get_absolute_url(self):
		return ('profiles_profile_detail', (), { 'username': self.user.username })
	get_absolute_url = models.permalink(get_absolute_url)
		
	def __str__(self):  
		  return "%s's profile" % self.user  
		  
class Location(models.Model): # all location details
	preferred_postcode = models.IntegerField(max_length=4)
	preferred_suburb = models.CharField(max_length=50)
	longitude = models.FloatField()
	latitude = models.FloatField()
	user_id = models.ForeignKey(User)
	is_tutoring_location = models.BooleanField(default=False) # only applies to tutors

class UOS(models.Model): # unit of study information
	unit_name = models.CharField(max_length=128)
	unit_id = models.CharField(max_length=8)    
	unit_description = models.TextField(max_length=200)

	def __str__(self):  
		  return self.unit_id

class Enrolled(models.Model):  # student details regarding all classes taken
	unit_id = models.ForeignKey(UOS)
	user_id = models.ForeignKey(User)
	is_complete = models.BooleanField()
	grade = models.IntegerField(blank = True)
	def __str__(self):  
		  return ' ' + self.unit_id.unit_name + ' (' + self.user_id.username + ')'

class UnitDetails(models.Model): # has all the information regarding what subjects a user will and wants to tutor + price
	user_id = models.ForeignKey(User)
	unit_id = models.ForeignKey(UOS)
	is_tutorable = models.BooleanField()
	is_tutoring = models.BooleanField()
	price = models.IntegerField(blank=True) # applies to tutors

class ClassTime(models.Model): # University Classes
	description = models.CharField(max_length = 56)
	start_time = models.DateTimeField(null = False)
	finish_time = models.DateTimeField(null = False)
	enrolled_id = models.ForeignKey(Enrolled)

class UnavailableTime(models.Model): # Times whree the tutor is unavailable 
	description = models.CharField(max_length = 56)
	start_time = models.DateTimeField(null = False)
	finish_time = models.DateTimeField(null = False)
	user_id = models.ForeignKey(User)

class SessionTime(models.Model): # Tutoring Session Time
	unit_id = models.ForeignKey(UOS,null=True)
	description = models.CharField(max_length = 56)
	start_time = models.DateTimeField(null = False)
	finish_time = models.DateTimeField(null = False)
	tutor_id = models.ForeignKey(User, related_name='tutor_id+')
	student_id = models.ForeignKey(User, related_name='student_id+')

class Review(models.Model): # review table
	RATING_CHOICES = (
					  (1,"1"),
					  (2,"2"),
					  (3,"3"),
					  (4,"4"),
					  (5,"5")
					  )
	student_id = models.ForeignKey(User, related_name = 'student_id+')
	tutor_id = models.ForeignKey(User,related_name='tutor_id+')
	comment = models.CharField(max_length=256)
	rating = models.IntegerField(choices = RATING_CHOICES,default = 3)

class Booking(models.Model):
	unit_id = models.ForeignKey(UOS)
	start_time = models.DateTimeField(null = False)
	finish_time = models.DateTimeField(null = False)
	tutor_id = models.ForeignKey(User, related_name='tutor_id+')
	student_id = models.ForeignKey(User, related_name='student_id+')
	is_rejected = models.BooleanField(default=False)
	is_confirmed = models.BooleanField(default=False)
	description = models.CharField(max_length = 56, default = '')
    