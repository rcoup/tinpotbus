from django.contrib import admin
from django.db.models import Max

from watch.models import Watch, Service, ServiceEvent


class ServiceEventInline(admin.TabularInline):
    model = ServiceEvent
    readonly_fields = ('maxx_ActualArrivalTime', 'maxx_ActualDepartureTime', 'maxx_ArrivalStatus', 'maxx_ExpectedArrivalTime', 'maxx_ExpectedDepartureTime', 'maxx_InCongestion', 'maxx_Monitored', 'maxx_TimeStamp',)
    fields = ('maxx_ActualArrivalTime', 'maxx_ActualDepartureTime', 'maxx_ArrivalStatus', 'maxx_ExpectedArrivalTime', 'maxx_ExpectedDepartureTime', 'maxx_InCongestion', 'maxx_Monitored', 'maxx_TimeStamp',)
    can_delete = False
    extra = 0


class WatchAdmin(admin.ModelAdmin):
    list_display = ('stop_id', 'route_id', 'is_active', 'last_updated', 'who_for',)
    list_filter = ('is_active',)
    actions = ['refresh']

    def refresh(self, request, queryset):
        Watch.objects.refresh(queryset)
        self.message_user(request, "Watches successfully refreshed.")
    refresh.short_description = "Update selected watches"

    def last_updated(self, instance):
        return instance.services.aggregate(Max('updated_at')).get('updated_at__max', None)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('scheduled_departure_time', 'watch__route_id', 'watch__stop_id', 'is_monitored', 'created_at', 'updated_at')
    list_filter = ('scheduled_departure_time', 'is_monitored', 'watch')
    ordering = ('-scheduled_departure_time', 'watch__stop_id', 'watch__route_id')
    inlines = [ServiceEventInline]

    def watch__route_id(self, instance):
        return instance.watch.route_id
    watch__route_id.short_description = 'Route'

    def watch__stop_id(self, instance):
        return instance.watch.stop_id
    watch__stop_id.short_description = 'Stop'

    def has_add_permission(self, request):
        return False


admin.site.register(Watch, WatchAdmin)
admin.site.register(Service, ServiceAdmin)
