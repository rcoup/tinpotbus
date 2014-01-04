# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Service.first_monitored_at'
        db.add_column(u'watch_service', 'first_monitored_at',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Service.first_monitored_at'
        db.delete_column(u'watch_service', 'first_monitored_at')


    models = {
        u'watch.service': {
            'Meta': {'object_name': 'Service'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'first_monitored_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
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