# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClassTime'
        db.create_table('tutablr_app_classtime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=56)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('finish_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('enrolled_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutablr_app.Enrolled'])),
        ))
        db.send_create_signal('tutablr_app', ['ClassTime'])

        # Adding model 'UnitDetails'
        db.create_table('tutablr_app_unitdetails', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('unit_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutablr_app.UOS'])),
            ('is_tutorable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_tutoring', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('price', self.gf('django.db.models.fields.IntegerField')(blank=True)),
        ))
        db.send_create_signal('tutablr_app', ['UnitDetails'])

        # Adding model 'Review'
        db.create_table('tutablr_app_review', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='student_id+', to=orm['auth.User'])),
            ('tutor_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tutor_id+', to=orm['auth.User'])),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=3)),
        ))
        db.send_create_signal('tutablr_app', ['Review'])

        # Adding model 'UOS'
        db.create_table('tutablr_app_uos', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('unit_id', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('unit_description', self.gf('django.db.models.fields.TextField')(max_length=200)),
        ))
        db.send_create_signal('tutablr_app', ['UOS'])

        # Adding model 'UnavailableTime'
        db.create_table('tutablr_app_unavailabletime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=56)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('finish_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('tutablr_app', ['UnavailableTime'])

        # Adding model 'Enrolled'
        db.create_table('tutablr_app_enrolled', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutablr_app.UOS'])),
            ('user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('grade', self.gf('django.db.models.fields.IntegerField')(blank=True)),
        ))
        db.send_create_signal('tutablr_app', ['Enrolled'])

        # Adding model 'UserProfile'
        db.create_table('tutablr_app_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('is_student_until', self.gf('django.db.models.fields.DateField')()),
            ('home_phone', self.gf('django.db.models.fields.IntegerField')(max_length=10)),
            ('mobile_phone', self.gf('django.db.models.fields.IntegerField')(max_length=11)),
            ('about_me', self.gf('django.db.models.fields.TextField')(max_length=400)),
            ('extra_details', self.gf('django.db.models.fields.TextField')(max_length=400)),
        ))
        db.send_create_signal('tutablr_app', ['UserProfile'])

        # Adding model 'Location'
        db.create_table('tutablr_app_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('preferred_postcode', self.gf('django.db.models.fields.IntegerField')(max_length=4)),
            ('preferred_suburb', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_tutoring_location', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('tutablr_app', ['Location'])

        # Adding model 'Booking'
        db.create_table('tutablr_app_booking', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutablr_app.UOS'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('finish_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('tutor_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tutor_id+', to=orm['auth.User'])),
            ('student_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='student_id+', to=orm['auth.User'])),
            ('is_rejected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('tutablr_app', ['Booking'])

        # Adding model 'SessionTime'
        db.create_table('tutablr_app_sessiontime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=56)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('finish_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('tutor_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tutor_id+', to=orm['auth.User'])),
            ('student_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='student_id+', to=orm['auth.User'])),
        ))
        db.send_create_signal('tutablr_app', ['SessionTime'])


    def backwards(self, orm):
        # Deleting model 'ClassTime'
        db.delete_table('tutablr_app_classtime')

        # Deleting model 'UnitDetails'
        db.delete_table('tutablr_app_unitdetails')

        # Deleting model 'Review'
        db.delete_table('tutablr_app_review')

        # Deleting model 'UOS'
        db.delete_table('tutablr_app_uos')

        # Deleting model 'UnavailableTime'
        db.delete_table('tutablr_app_unavailabletime')

        # Deleting model 'Enrolled'
        db.delete_table('tutablr_app_enrolled')

        # Deleting model 'UserProfile'
        db.delete_table('tutablr_app_userprofile')

        # Deleting model 'Location'
        db.delete_table('tutablr_app_location')

        # Deleting model 'Booking'
        db.delete_table('tutablr_app_booking')

        # Deleting model 'SessionTime'
        db.delete_table('tutablr_app_sessiontime')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tutablr_app.booking': {
            'Meta': {'object_name': 'Booking'},
            'finish_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_rejected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'student_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'student_id+'", 'to': "orm['auth.User']"}),
            'tutor_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tutor_id+'", 'to': "orm['auth.User']"}),
            'unit_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tutablr_app.UOS']"})
        },
        'tutablr_app.classtime': {
            'Meta': {'object_name': 'ClassTime'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '56'}),
            'enrolled_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tutablr_app.Enrolled']"}),
            'finish_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'tutablr_app.enrolled': {
            'Meta': {'object_name': 'Enrolled'},
            'grade': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unit_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tutablr_app.UOS']"}),
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'tutablr_app.location': {
            'Meta': {'object_name': 'Location'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_tutoring_location': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'preferred_postcode': ('django.db.models.fields.IntegerField', [], {'max_length': '4'}),
            'preferred_suburb': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'tutablr_app.review': {
            'Meta': {'object_name': 'Review'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'student_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'student_id+'", 'to': "orm['auth.User']"}),
            'tutor_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tutor_id+'", 'to': "orm['auth.User']"})
        },
        'tutablr_app.sessiontime': {
            'Meta': {'object_name': 'SessionTime'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '56'}),
            'finish_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'student_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'student_id+'", 'to': "orm['auth.User']"}),
            'tutor_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tutor_id+'", 'to': "orm['auth.User']"})
        },
        'tutablr_app.unavailabletime': {
            'Meta': {'object_name': 'UnavailableTime'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '56'}),
            'finish_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'tutablr_app.unitdetails': {
            'Meta': {'object_name': 'UnitDetails'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_tutorable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_tutoring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'price': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'unit_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tutablr_app.UOS']"}),
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'tutablr_app.uos': {
            'Meta': {'object_name': 'UOS'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'unit_description': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            'unit_id': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'unit_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'tutablr_app.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'about_me': ('django.db.models.fields.TextField', [], {'max_length': '400'}),
            'extra_details': ('django.db.models.fields.TextField', [], {'max_length': '400'}),
            'home_phone': ('django.db.models.fields.IntegerField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_student_until': ('django.db.models.fields.DateField', [], {}),
            'mobile_phone': ('django.db.models.fields.IntegerField', [], {'max_length': '11'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['tutablr_app']