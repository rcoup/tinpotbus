# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Watch'
        db.create_table(u'watch_watch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stop_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('route_id', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
        ))
        db.send_create_signal(u'watch', ['Watch'])

        # Adding model 'Service'
        db.create_table(u'watch_service', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('watch', self.gf('django.db.models.fields.related.ForeignKey')(related_name='services', to=orm['watch.Watch'])),
            ('scheduled_departure_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('is_monitored', self.gf('django.db.models.fields.BooleanField')(db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('monitored_departure_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_data_json', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal(u'watch', ['Service'])


    def backwards(self, orm):
        # Deleting model 'Watch'
        db.delete_table(u'watch_watch')

        # Deleting model 'Service'
        db.delete_table(u'watch_service')


    models = {
        u'watch.service': {
            'Meta': {'object_name': 'Service'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_monitored': ('django.db.models.fields.BooleanField', [], {'db_index': 'True'}),
            'last_data_json': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'monitored_departure_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'scheduled_departure_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {}),
            'watch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'services'", 'to': u"orm['watch.Watch']"})
        },
        u'watch.watch': {
            'Meta': {'object_name': 'Watch'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'route_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'stop_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['watch']