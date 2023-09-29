from datetime import timedelta

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils import timezone

from .connector import from_xlsx_file_data_to_server_create_data
from .models import Product, Monitoring, Document, Chain, Config
from .services import create_document_on_server


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
        return (obj.date + timedelta(hours=3)).strftime('%d.%m.%Y')

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
    list_display = ('get_name_organization', 'document_number', 'get_date')
    readonly_fields = ('document_number', 'date', 'organization', 'response')

    def get_name_organization(self, obj):
        return obj.organization.name

    get_name_organization.short_description = 'Организация'

    def get_date(self, obj):
        return (obj.date + timedelta(hours=3)).strftime('%d.%m.%Y')

    get_date.short_description = 'Дата создания'

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        document = from_xlsx_file_data_to_server_create_data(obj.file)
        if document is not None:
            result, response = create_document_on_server(document)
            if result:
                obj.document_number = response['response']['documentNumber']
                obj.organization = Chain.objects.first()
                obj.response = response
                obj.file.delete()
                messages.set_level(request, messages.SUCCESS)
                messages.success(request, 'Документ успешно загружен.')
                super().save_model(request, obj, form, change)
            else:
                obj.organization = Chain.objects.first()
                obj.response = response
                obj.file.delete()
                messages.set_level(request, messages.ERROR)
                messages.error(request, 'Документ не обработан, проверьте файл!')
                super().save_model(request, obj, form, change)
        else:
            messages.set_level(request, messages.ERROR)
            messages.error(request, 'Документ не обработан, проверьте файл!')


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin):
    list_display = ('name', 'server_url', 'server_port', 'server_login', 'server_password')


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
