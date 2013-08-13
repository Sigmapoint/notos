# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PushResult'
        db.create_table(u'notos_pushresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('response_code', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'notos', ['PushResult'])

        # Adding model 'ScheduledPush'
        db.create_table(u'notos_scheduledpush', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scheduled_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('send_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('canceled_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('registration_id', self.gf('django.db.models.fields.CharField')(max_length=4095)),
            ('result', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['notos.PushResult'], unique=True, null=True, blank=True)),
            ('attempt_no', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('data', self.gf('json_field.fields.JSONField')(default=u'null')),
        ))
        db.send_create_signal(u'notos', ['ScheduledPush'])


    def backwards(self, orm):
        # Deleting model 'PushResult'
        db.delete_table(u'notos_pushresult')

        # Deleting model 'ScheduledPush'
        db.delete_table(u'notos_scheduledpush')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'notos.pushresult': {
            'Meta': {'object_name': 'PushResult'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'response_code': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'notos.scheduledpush': {
            'Meta': {'object_name': 'ScheduledPush'},
            'attempt_no': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'canceled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'data': ('json_field.fields.JSONField', [], {'default': "u'null'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '4095'}),
            'result': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['notos.PushResult']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'scheduled_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'send_at': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['notos']