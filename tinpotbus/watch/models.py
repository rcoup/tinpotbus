import datetime
import json
import logging
import random
import re
import time

from django.conf import settings
from django.db import models
from django.utils import timezone
import pytz
import requests


# make our API requests look like jQuery
api_nonce = ['jQuery' + str(random.random()).replace('0.', ''), int(time.time() * 1000)]
api_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8) AppleWebKit/536.25 (KHTML, like Gecko) Version/6.0 Safari/536.25',
    'Referer': 'http://www.maxx.co.nz/',
    'Accept-Encoding': 'gzip,deflate',
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

        stats = [0, 0]
        for url in self.get_api_urls(queryset):
            try:
                L.debug('Hitting Maxx API: %s', url)
                r = requests.get(url, headers=api_headers, timeout=10)
                if r.status_code == 200:
                    L.debug('GET %s status=%s', url, r.status_code)
                    try:
                        r_jsonp = r.text
                        r_json = r_jsonp[r_jsonp.index("(")+1:r_jsonp.rindex(")")]
                        data = json.loads(r_json)
                    except Exception as e:
                        L.error("Decoding JSONP: %s source=%s", e, repr(r.text))
                        raise

                    if 'Movements' not in data or not data['Movements']:
                        continue

                    L.debug("Got %s movements", len(data['Movements']))
                    if len(data['Movements']):
                        stats[0] += 1

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
                    stats[1] += 1
            except Exception as e:
                L.error('GET %s error=%s', url, e)
                if settings.DEBUG:
                    raise

        if sum(stats):
            return stats[0] / float(stats[0] + stats[1])
        else:
            return 1.0

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
        service.updated_at = movement['TimeStamp'] or timezone.now()
        service.save()

        if (movement['ActualDepartureTime'] - timezone.now()) <= datetime.timedelta(hours=1):
            service.create_event(movement)

        return service


class Service(models.Model):
    watch = models.ForeignKey(Watch, related_name='services')
    scheduled_departure_time = models.DateTimeField(db_index=True)
    is_monitored = models.BooleanField(db_index=True, default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __unicode__(self):
        return u"%s: %s" % (self.watch, timezone.localtime(self.scheduled_departure_time).isoformat())

    def create_event(self, movement):
        e = ServiceEvent(service=self)
        for k, v in movement.items():
            field = 'maxx_%s' % k
            setattr(e, field, v)
        e.save()
        return e


class ServiceEvent(models.Model):
    service = models.ForeignKey(Service, related_name='events', db_index=True)
    maxx_ActualArrivalTime = models.DateTimeField('ActualArrivalTime', null=True, db_index=True)
    maxx_ActualDepartureTime = models.DateTimeField('ActualDepartureTime', null=True, db_index=True)
    maxx_ArrivalStatus = models.CharField('ArrivalStatus', max_length=200, blank=True, null=True, db_index=True)
    maxx_ExpectedArrivalTime = models.DateTimeField('ExpectedArrivalTime', null=True, db_index=True)
    maxx_ExpectedDepartureTime = models.DateTimeField('ExpectedDepartureTime', null=True, db_index=True)
    maxx_InCongestion = models.NullBooleanField('InCongestion', null=True, db_index=True)
    maxx_Monitored = models.NullBooleanField('Monitored', null=True, db_index=True)
    maxx_TimeStamp = models.DateTimeField('TimeStamp', null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created_at',)

    def __unicode__(self):
        return timezone.localtime(self.created_at).isoformat()
