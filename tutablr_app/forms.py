from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.admin import widgets 
from tutablr_app.models import *
from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.extras.widgets import SelectDateWidget

class ProfileForm(ModelForm):
 
	def __init__(self, *args, **kwargs):
		super(ProfileForm, self).__init__(*args, **kwargs)
		try:
			self.fields['email'].initial = self.instance.user.email
			self.fields['first_name'].initial = self.instance.user.first_name
			self.fields['last_name'].initial = self.instance.user.last_name
		except User.DoesNotExist:
			pass
 
	email = forms.EmailField(label="Primary email",help_text='')
	first_name = forms.CharField(label="First name",help_text='')
	last_name = forms.CharField(label="Last name",help_text='')
	class Meta:
	  model = UserProfile
	  exclude = ('user',)        
 
	def save(self, *args, **kwargs):
		"""
		Update the primary email address on the related User object as well.
		"""
		u = self.instance.user
		u.email = self.cleaned_data['email']
		u.first_name = self.cleaned_data['first_name']
		u.last_name = self.cleaned_data['last_name']
		u.save()
		profile = super(ProfileForm, self).save(*args,**kwargs)
		return profile

class YourRegistrationForm(RegistrationForm):
	def save(self, profile_callback=None):
		new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
		password=self.cleaned_data['password1'],
		email = self.cleaned_data['email'], 
		first_name = self.cleaned_data['first_name'], 
		last_name=self.cleaned_data['last_name'])
		new_user.save()
		new_profile = Profile(user=new_user)
		new_profile.save()
		return new_user

		
class addBookingForm(forms.Form):
	#print('HERHEHRHERHEHRHRRH')
	date = forms.DateField()
	date.widget.format = '%d/%m/%Y'
	date.widget.attrs.update({'class':'datePicker', 'readonly':'true'})
	start_time = forms.TimeField()
	finish_time = forms.TimeField()
	UoS = forms.ChoiceField()
	description = forms.CharField(max_length=56)
	#creator_id = forms.IntegerField()
	def __init__(self, *args, **kwargs):
		tutor_id = kwargs.pop('tutor_id',0)
		super(addBookingForm, self).__init__(*args, **kwargs)
		choices = [(o.unit_id.unit_id, str(o.unit_id.unit_id)) for o in UnitDetails.objects.filter(user_id = tutor_id, is_tutorable = True)]
		self.fields['UoS'] = forms.ChoiceField(widget = forms.Select(), initial=choices[0][0], choices=choices, required=True)
		#self.fields['creator_id'].widget = forms.HiddenInput()


"""
class searchForm(forms.Form):
	UoS = forms.ChoiceField()
	price_from = forms.IntegerField(initial = 0, required=False)
	price_to = forms.IntegerField(initial=30, required=False)
	distance_choices = [(5, '5 km'), (10, '10km'), (15, '15km'), (25, '25km'), (1000, 'Any')]
	distance = forms.ChoiceField(widget=forms.Select(), choices=distance_choices, initial=choices[0][5], required=False)
	#only if students
	grade_from_choices = [('HD', 'HD'), ('D', 'D'), ('C', 'C')]
	grade_from = forms.ChoiceField(widget=forms.Select(), choices=grade_choices, initial=choices[0][0], required=True)
	students_only = forms.BooleanField(label="StudentsOnly")
	rating_from_choices = [(5, '5 Stars'), (4, '4 Stars'), (3, '3 Stars'), (2, '2 Stars'), (1, '1 Star'), (0, 'Any')]
	rating_from = forms.ChoiceField(widget=forms.Select(), choices=rating_from_choices, initial=choices[0][5], required=True)
 	def __init__(self, *args, **kwargs):
  		user_id=kwargs.pop('user_id',0)
  		super(addBookingForm, self).__init__(*args, **kwargs)
  		uos_choices = [(o.unit_id.unit_id, str(o.unit_id.unit_id)) for o in Enrolled.objects.filter(user_id = user_id, is_complete=False)]
  		self.fields['UoS'] = forms.ChoiceField(widget = forms.Select(), initial=choices[0][0], choices=choices, required=True)
"""	


class LocationForm (ModelForm):
	class Meta:
		model = Location

class TutorLocationForm (ModelForm):
	class Meta:
		model = TutoringLocation
