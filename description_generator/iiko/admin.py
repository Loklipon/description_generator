from datetime import timedelta

from django.contrib import admin

from iiko.models import ServerLog, UserLog


@admin.register(ServerLog)
class ServerLogAdmin(admin.ModelAdmin):
    list_display = ('url', 'get_time', 'request', 'response_status')

    def get_time(self, obj):
        return (obj.time + timedelta(hours=3)).strftime('%H:%M:%S %d.%m.%Y')

    get_time.short_description = 'Время'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ('get_time', 'status')

    def get_time(self, obj):
        return (obj.time + timedelta(hours=3)).strftime('%H:%M:%S %d.%m.%Y')

    get_time.short_description = 'Время'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
