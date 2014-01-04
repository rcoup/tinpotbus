import datetime
import json
import logging
import random
import re
import time

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
import pytz
import requests


# make our API requests look like jQuery
api_nonce = ['jQuery' + str(random.random()).replace('0.', ''), int(time.time() * 1000)]
api_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8) AppleWebKit/536.25 (KHTML, like Gecko) Version/6.0 Safari/536.25',
    'Referer': 'http://www.maxx.co.nz/',
}


class WatchManager(models.Manager):
    API_BASE_URL = 'http://api.maxx.co.nz/RealTime/v2/Departures/Stop/%(stop_id)s?callback=%(callback)s&hours=2&_=%(timestamp)s'

    def get_api_urls(self, queryset):
        stop_ids = set(queryset.values_list('stop_id', flat=True))

        urls = []
        for stop_id in stop_ids:
            callback = "%s_%s" % (api_nonce[0], api_nonce[1])
            api_nonce[1] += random.randint(1, 50)

            url = self.API_BASE_URL % {
                'stop_id': stop_id,
                'callback': callback,
                'timestamp': int((time.time() + random.random()) * 1000),
            }
            urls.append(url)

        return urls

    def refresh(self, queryset=None):
        L = logging.getLogger('tinpotbus.watch.refresh')
        if not queryset:
            queryset = self.get_query_set().filter(is_active=True)

        for url in self.get_api_urls(queryset):
            try:
                L.debug('Hitting Maxx API: %s', url)
                r = requests.get(url, headers=api_headers, timeout=10)
                if r.status_code == 200:
                    L.debug('GET %s status=%s', url, r.status_code)
                    try:
                        r_jsonp = r.text
                        r_json = r_jsonp[r_jsonp.index("(")+1 : r_jsonp.rindex(")")]
                        data = json.loads(r_json)
                    except Exception as e:
                        L.error("Decoding JSONP: %s source=%s", e, repr(r.text))
                        raise

                    L.debug("Got %s movements", len(data['Movements']))
                    for movement in data['Movements']:
                        # {
                        #     ActualArrivalTime: "/Date(1388781780000)/",
                        #     ActualDepartureTime: "/Date(1388781780000)/",
                        #     ArrivalBoardingActivity: "alighting",
                        #     ArrivalPlatformName: null,
                        #     ArrivalStatus: "noReport",
                        #     DepartureBoardingActivity: "boarding",
                        #     DeparturePlatformName: null,
                        #     DestinationDisplay: "MIDTOWN",
                        #     ExpectedArrivalTime: null,
                        #     ExpectedDepartureTime: null,
                        #     InCongestion: false,
                        #     Monitored: false,
                        #     Route: "392",
                        #     Stop: "7201",
                        #     TimeStamp: "/Date(1388781639717)/",
                        #     VehicleJourneyName: null
                        # }

                        for date_field in ('ActualArrivalTime', 'ActualDepartureTime', 'ExpectedArrivalTime', 'ExpectedDepartureTime', 'TimeStamp'):
                            movement[date_field] = self._parse_js_date(movement[date_field])

                        try:
                            watch = queryset.get(stop_id=movement['Stop'], route_id=movement['Route'], is_active=True)
                        except Watch.DoesNotExist:
                            continue

                        L.debug("Updating watch: %s %s", watch.pk, str(watch))
                        try:
                            watch.create_or_update_service(movement)
                        except Exception as e:
                            L.error("Updating watch %s: %s", watch.pk, e)
                            raise
                else:
                    L.warning('GET %s status=%s', url, r.status_code)
            except Exception as e:
                L.error('GET %s error=%s', url, e)
                if settings.DEBUG:
                    raise


    def _parse_js_date(self, value):
        """ Parse a .NET Javascript-serialized date (eg. "/Date(1354011247940)/") to a datetime object """
        if not value:
            return None

        m = re.match(r'/Date\((\d+)\)/$', value)
        if not m:
            raise ValueError("Invalid JS date: '%s'" % value)

        d = datetime.datetime.fromtimestamp(int(m.group(1))/1000.0)
        d = timezone.make_aware(d, pytz.timezone("Pacific/Auckland"))
        
        return d


class Watch(models.Model):
    stop_id = models.IntegerField('Stop', db_index=True)
    route_id = models.CharField('Route', max_length=20, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    who_for = models.TextField(blank=True)

    objects = WatchManager()

    class Meta:
        verbose_name_plural = 'Watches'

    def __unicode__(self):
        return u"%s @ Stop %d" % (self.route_id, self.stop_id)

    def create_or_update_service(self, movement):
        try:
            service = self.services.get(scheduled_departure_time=movement['ActualDepartureTime'])
        except Service.DoesNotExist:
            service = Service(watch=self, scheduled_departure_time=movement['ActualDepartureTime'], created_at=movement['TimeStamp'])

        service.is_monitored = service.is_monitored or movement['Monitored']
        if movement['ExpectedDepartureTime']:
            if not service.monitored_departure_time:
                service.first_monitored_at = movement['TimeStamp']
            service.monitored_departure_time = movement['ExpectedDepartureTime']
            service.last_monitored_at = movement['ExpectedDepartureTime']
        elif service.monitored_departure_time:
            service.last_monitored_at = service.updated_at # previous time

        service.last_data = movement
        service.updated_at = movement['TimeStamp']
        service.save()

        return service


class Service(models.Model):
    watch = models.ForeignKey(Watch, related_name='services')
    scheduled_departure_time = models.DateTimeField(db_index=True)
    is_monitored = models.BooleanField(db_index=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    first_monitored_at = models.DateTimeField(null=True, help_text="Time when the monitoring started.")
    last_monitored_at = models.DateTimeField(null=True, help_text="Last time we saw monitoring before it stopped.")
    monitored_departure_time = models.DateTimeField(null=True)
    last_data_json = models.TextField(default='')

    def __unicode__(self):
        return u"%s: %s" % (self.watch, self.scheduled_departure_time.isoformat())

    def _last_data_get(self):
        if self.last_data_json:
            return json.loads(self.last_data_json)
        else:
            return None

    def _last_data_set(self, value):
        if not value:
            self.last_data_json = ''
        else:
            self.last_data_json = json.dumps(value, cls=DjangoJSONEncoder)

    last_data = property(_last_data_get, _last_data_set)
