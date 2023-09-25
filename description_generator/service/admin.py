from datetime import timedelta

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path

from .connector import from_xlsx_file_data_to_server_create_data
from .models import Product, Monitoring, Document, Department
from .services import create_nomenclature_elements, check_charts, create_document_on_server, create_organizations


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

    get_check.boolean = True

    get_check.short_description = 'Выполнено'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('load_data/', self.load_data)]
        return my_urls + urls

    def load_data(self, request):
        create_organizations()
        create_nomenclature_elements()
        check_charts()
        self.message_user(request, 'Данные успешно загружены')
        return HttpResponseRedirect('../')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('organization', 'document_number', 'get_date')
    readonly_fields = ('document_number', 'date', 'organization', 'response')

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
                obj.organization = Department.objects.get(uuid=document.items[0].department_id)
                obj.response = response
                obj.file.delete()
                messages.set_level(request, messages.SUCCESS)
                messages.success(request, 'Документ успешно загружен.')
                super().save_model(request, obj, form, change)
            else:
                obj.organization = Department.objects.get(uuid=document.items[0].department_id)
                obj.response = response
                obj.file.delete()
                messages.set_level(request, messages.ERROR)
                messages.error(request, 'Документ не обработан, проверьте файл!')
                super().save_model(request, obj, form, change)
        else:
            messages.set_level(request, messages.ERROR)
            messages.error(request, 'Документ не обработан, проверьте файл!')


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


admin.site.site_header = 'Хлеб Насущный | Description Creator'

admin.site.index_title = ''