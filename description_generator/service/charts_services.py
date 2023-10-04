import json
import xml.etree.ElementTree as ET
from typing import Tuple, Union

from pydantic import parse_obj_as

from iiko.models import UserLog
from iiko.server import IikoServer
from .dataclasses.charts import ResponseData
from .dataclasses.nomenclature import ProductData
from .models import Product, Monitoring, Department, Chain

FILE_ERRORS_MESSAGES = {
    'empty_field': 'Не заполнено одно из полей. Строки: ',
    'wrong_type_of_filed': 'В одном из полей неверный тип данных. Строки: ',
    'no_product': 'В номенклатуре нет продукта с таким артикулом. Строки: ',
    'a_lot_of_products': 'В номенклатуре две или более единицы таким артикулом. Строки: ',
    'no_department': 'Нет торговой точки с таким названием. Строки: ',
    'any_other': 'У организации две или более торговых точек с одинаковым названием. Строки: '
}


def get_nomenclature() -> bool:
    """
    Создание и/или обновление всех элементов номенклатуры чейна в БД.
    Обновление по uuid элемента.
    """
    UserLog.objects.create(status='Началась загрузка элементов номенклатуры')
    if Product.objects.exists():
        Product.objects.all().delete()
    iiko_server = IikoServer(Chain.objects.first())
    response = iiko_server.products_list(product=None)
    if response.status_code == 200:
        products = parse_obj_as(list[ProductData], json.loads(response.text))
        for product in products:
            Product.objects.update_or_create(
                uuid=product.uuid,
                defaults={
                    'name': product.name,
                    'description': product.description,
                    'type': product.type,
                    'num': product.num,
                    'checked': False
                }
            )
        Product.objects.filter(checked=True).delete()
        UserLog.objects.create(status='Загрузка элементов номенклатуры выполнена успешно')
        return True
    else:
        UserLog.objects.create(status='Загрузка элементов номенклатуры не выполнена')
        return False


def change_product_description_on_server(product: Product,
                                         description: str,
                                         iiko_server: IikoServer) -> bool:
    """
    Изменение описания продукта на сервере.
    В случае успеха - изменение в БД.
    """
    response = iiko_server.products_list(product)
    if response.status_code == 200:
        response_data = json.loads(response.text)
        product_data = response_data[0]
        product_data['description'] = description
        data_to_update = json.dumps(product_data)
        product_update_response = iiko_server.product_update(data_to_update)
        if product_update_response.status_code == 200:
            if json.loads(product_update_response.text)['result'] == 'SUCCESS':
                return True
            return False
    return False


def create_and_check_charts_descriptions(items: list) -> Union[Tuple[list, str], Tuple[None, None]]:
    """
    Проверка наличия описаний элементов ТТК.
    Создание описания блюда.
    """
    product_list = []
    description_list = []
    for item in items:
        try:
            product = Product.objects.get(uuid=item.uuid)
        except Product.DoesNotExist:
            return None, None
        if len(product.description) == 0:
            product_list.append(product.name)
        else:
            description_list.append(product.description)
    description = '; '.join(description_list)
    return product_list, description


def check_charts() -> None:
    """
    Основная логика проверки ТТК.
    """
    UserLog.objects.create(status='Началась проверка ТТК всех блюд')
    try:
        products = Product.objects.filter(type='DISH', checked=False)
        iiko_server = IikoServer(Chain.objects.first())
        try:
            for product in products:
                product.checked = True
                product.save()
                if product.num is None:
                    Monitoring.objects.create(
                        dish_name=product.name,
                        num=product.num,
                        status='Ошибка',
                        error='У блюда отсутствует артикул'
                    )
                else:
                    monitoring = Monitoring.objects.create(
                        dish_name=product.name,
                        num=product.num)
                    response = iiko_server.chart(product)
                    try:
                        if response.status_code == 200:
                            response_data = ResponseData.parse_raw(response.text)
                            if response_data is not None:
                                chart = response_data.prepared_charts[0]
                                if chart is not None:
                                    items = chart.items
                                    if len(items) != 0:
                                        empty_description_product_list, dish_description = create_and_check_charts_descriptions(
                                            items)
                                        if empty_description_product_list is None and dish_description is None:
                                            monitoring.status = 'Ошибка'
                                            monitoring.error = 'В составе ТТК содержится элемент, отсутствующий в номенклатуре'
                                            monitoring.save()
                                        else:
                                            if len(empty_description_product_list) != 0:
                                                monitoring.status = 'Ошибка'
                                                monitoring.error = 'Не заполнено поле "Описание" у ингредиентов: ' + '; '.join(
                                                    empty_description_product_list)
                                                monitoring.save()
                                            else:
                                                if change_product_description_on_server(product, dish_description,
                                                                                        iiko_server):
                                                    monitoring.status = 'Успешно'
                                                    monitoring.save()
                                                    product.description = dish_description
                                                    product.save()
                                                else:
                                                    monitoring.status = 'Ошибка'
                                                    monitoring.error = 'Не удалось изменить описание у блюда'
                                                    monitoring.save()
                                    else:
                                        monitoring.status = 'Ошибка'
                                        monitoring.error = 'ТТК не заполнена'
                                        monitoring.save()
                                else:
                                    monitoring.status = 'Ошибка'
                                    monitoring.error = 'У блюда отсутствует ТТК'
                                    monitoring.save()
                            else:
                                monitoring.status = 'Ошибка'
                                monitoring.error = 'У блюда отсутствует ТТК'
                                monitoring.save()
                        else:
                            monitoring.status = 'Ошибка'
                            monitoring.error = 'Ошибка исполнения программы'
                            monitoring.save()
                    except Exception as e:
                        print(e)
                        continue
        except Exception as e:
            print(e)
            iiko_server.logout()
            UserLog.objects.create(status='Проверка ТТК была прервана')
            return
        iiko_server.logout()
        UserLog.objects.create(status='Проверка ТТК выполнена успешно')
    except Exception as e:
        print(e)
        UserLog.objects.create(status='Проверка ТТК была прервана')


def get_departments() -> bool:
    """
    Создание и/или обновление торговых точек в БД.
    Обновление по uuid торговой точки.
    """
    if Chain.objects.exists():
        UserLog.objects.create(status='Началась загрузка торговых точек')
        iiko_server = IikoServer(Chain.objects.first())
        response = iiko_server.departments()
        if response.status_code == 200:
            departments_xml_tree = ET.ElementTree(ET.fromstring(response.text))
            for item in departments_xml_tree.iter('corporateItemDto'):
                department_type = item.find('type').text
                if department_type == 'DEPARTMENT':
                    department_name = item.find('name').text
                    department_uuid = item.find('id').text
                    Department.objects.update_or_create(
                        uuid=department_uuid,
                        defaults={'name': department_name})
            UserLog.objects.create(status='Загрузка торговых точек выполнена успешно')
            return True
        else:
            UserLog.objects.create(status='Загрузка торговых точек не выполнена')
            return False
