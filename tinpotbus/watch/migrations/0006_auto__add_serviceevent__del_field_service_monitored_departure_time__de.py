# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ServiceEvent'
        db.create_table(u'watch_serviceevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['watch.Service'])),
            ('maxx_ActualArrivalTime', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('maxx_ActualDepartureTime', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('maxx_ArrivalStatus', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=200, null=True, blank=True)),
            ('maxx_ExpectedArrivalTime', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('maxx_ExpectedDepartureTime', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('maxx_InCongestion', self.gf('django.db.models.fields.NullBooleanField')(db_index=True, null=True, blank=True)),
            ('maxx_Monitored', self.gf('django.db.models.fields.NullBooleanField')(db_index=True, null=True, blank=True)),
            ('maxx_TimeStamp', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'watch', ['ServiceEvent'])

        # Deleting field 'Service.monitored_departure_time'
        db.delete_column(u'watch_service', 'monitored_departure_time')

        # Deleting field 'Service.last_monitored_at'
        db.delete_column(u'watch_service', 'last_monitored_at')

        # Deleting field 'Service.last_data_json'
        db.delete_column(u'watch_service', 'last_data_json')

        # Deleting field 'Service.first_monitored_at'
        db.delete_column(u'watch_service', 'first_monitored_at')

        orm.Service.objects.all().delete()

    def backwards(self, orm):
        # Deleting model 'ServiceEvent'
        db.delete_table(u'watch_serviceevent')

        # Adding field 'Service.monitored_departure_time'
        db.add_column(u'watch_service', 'monitored_departure_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Adding field 'Service.last_monitored_at'
        db.add_column(u'watch_service', 'last_monitored_at',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Adding field 'Service.last_data_json'
        db.add_column(u'watch_service', 'last_data_json',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Service.first_monitored_at'
        db.add_column(u'watch_service', 'first_monitored_at',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)


    models = {
        u'watch.service': {
            'Meta': {'object_name': 'Service'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_monitored': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'scheduled_departure_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {}),
            'watch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'services'", 'to': u"orm['watch.Watch']"})
        },
        u'watch.serviceevent': {
            'Meta': {'ordering': "('created_at',)", 'object_name': 'ServiceEvent'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maxx_ActualArrivalTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'maxx_ActualDepartureTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'maxx_ArrivalStatus': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'maxx_ExpectedArrivalTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'maxx_ExpectedDepartureTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'maxx_InCongestion': ('django.db.models.fields.NullBooleanField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'maxx_Monitored': ('django.db.models.fields.NullBooleanField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'maxx_TimeStamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': u"orm['watch.Service']"})
        },
        u'watch.watch': {
            'Meta': {'object_name': 'Watch'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'route_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'stop_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'who_for': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['watch']