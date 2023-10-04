from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils import timezone

from .document_services import document_object_handler
from .models import Product, Monitoring, Document, Chain, Config


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'num', 'description')
    search_fields = ('name', 'num')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Monitoring)
class MonitoringAdmin(admin.ModelAdmin):
    list_display = ('dish_name', 'num', 'status', 'error', 'get_date', 'get_check')
    change_list_template = 'admin/monitoring_change_list.html'

    def get_date(self, obj):
        return timezone.localtime(obj.time).strftime('%d.%m.%Y')

    get_date.short_description = 'Дата выгрузки'

    def get_check(self, obj):
        if obj.status == 'Успешно':
            return True
        if obj.status == 'Ошибка':
            return False
        if not obj.status:
            return False

    get_check.boolean = True

    get_check.short_description = 'Выполнено'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('load_data/', self.load_data)]
        return my_urls + urls

    def load_data(self, request):
        if timezone.localtime(timezone.now()).hour in [23, 0, 1, 2]:
            messages.error(request, 'В данное время нельзя осуществить ручную загрузку данных')
            return HttpResponseRedirect('../')
        config = Config.objects.first()
        if config.check_button:
            messages.error(request, 'Предыдущая загрузка данных еще не завершена')
            return HttpResponseRedirect('../')
        config.check_button = True
        config.save()
        self.message_user(request, 'Началась загрузка данных')
        return HttpResponseRedirect('../')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'get_time', 'check_file',
                    'check_document', 'document_number')
    fields = ('file',)

    def get_time(self, obj):
        return timezone.localtime(obj.date).strftime('%H:%M:%S %d.%m.%y')

    get_time.short_description = 'Время загрузки'

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if timezone.localtime(timezone.now()).hour in [23, 0, 1, 2]:
            messages.set_level(request, messages.ERROR)
            messages.error(request, 'В данное время нельзя осуществить загрузку приказа.')
            return HttpResponseRedirect('../')
        if Config.objects.first().check_button:
            messages.set_level(request, messages.ERROR)
            messages.error(request, 'Во время анализа ТТК нельзя создать приказ.')
            return HttpResponseRedirect('../')
        obj = document_object_handler(obj)
        if obj.check_file and obj.check_document:
            messages.success(request, 'Файл полностью обработан. Приказ создан.')
        if not obj.check_file and obj.check_document:
            messages.warning(request, 'Файл обработан частично. Приказ создан.')
        if obj.check_file and obj.check_document is False:
            messages.error(request, 'Файл полностью обработан. Приказ не создан.')
        if not obj.check_file and obj.check_document is False:
            messages.error(request, 'Файл обработан частично. Приказ не создан.')
        if not obj.check_file and obj.check_document is None:
            messages.error(request, 'Файл не обработан. Приказ не создан.')
            obj.check_document = False
        messages.set_level(request, messages.WARNING)
        super().save_model(request, obj, form, change)


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin):
    list_display = ('name', 'server_url', 'server_port', 'server_login', 'server_password')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# @admin.register(Department)
# class DepartmentAdmin(admin.ModelAdmin):
#     list_display = ('name', 'uuid')
#
#     def has_add_permission(self, request):
#         return False
#
#     def has_change_permission(self, request, obj=None):
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         return False


admin.site.site_header = 'Хлеб Насущный | Description Generator'

admin.site.index_title = ''
