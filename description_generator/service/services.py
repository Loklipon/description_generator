import json
import xml.etree.ElementTree as ET
from typing import Tuple, Union

from pydantic import parse_obj_as

from iiko.models import UserLog
from iiko.server import IikoServer
from .dataclasses.charts import ResponseData
from .dataclasses.document import DocumentData
from .dataclasses.nomenclature import ProductData
from .models import Product, Monitoring, Department


def create_nomenclature_elements() -> None:
    """
    Создание и/или обновление всех элементов номенклатуры чейна в БД.
    Обновление по uuid элемента.
    """
    UserLog.objects.create(status='Началась загрузка элементов номенклатуры')
    iiko_server = IikoServer()
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
                    'num': product.num}
            )
        UserLog.objects.create(status='Загрузка элементов номенклатуры выполнена успешно')
    else:
        UserLog.objects.create(status='Загрузка элементов номенклатуры не выполнена')


def change_product_description(
        product: Product,
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


def create_and_check_descriptions(items: list) -> Union[Tuple[list, str], Tuple[None, None]]:
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
    products = Product.objects.filter(type='DISH')
    iiko_server = IikoServer()
    for product in products:
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
            if response.status_code == 200:
                response_data = ResponseData.parse_raw(response.text)
                chart = response_data.prepared_charts[0]
                if chart is not None:
                    items = chart.items
                    if len(items) != 0:
                        empty_description_product_list, dish_description = create_and_check_descriptions(items)
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
                                if change_product_description(product, dish_description, iiko_server):
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
                monitoring.error = 'Ошибка исполнения программы'
                monitoring.save()
                UserLog.objects.create(status='Проверка ТТК не выполнена')
    iiko_server.logout()
    UserLog.objects.create(status='Проверка ТТК выполнена успешно')


def create_organizations():
    """
    Создание и/или обновление торговых точек в БД.
    Обновление по uuid торговой точки.
    """
    UserLog.objects.create(status='Началась загрузка торговых точек')
    iiko_server = IikoServer()
    response = iiko_server.departments()
    if response.status_code == 200:
        departments_xml_tree = ET.ElementTree(ET.fromstring(response.text))
        for item in departments_xml_tree.iter('corporateItemDto'):
            department_name = item.find('name').text
            department_uuid = item.find('id').text
            Department.objects.update_or_create(
                uuid=department_uuid,
                defaults={'name': department_name})
        UserLog.objects.create(status='Загрузка торговых точек выполнена успешно')
    else:
        UserLog.objects.create(status='Загрузка торговых точек не выполнена')


def create_document_on_server(document: DocumentData) -> Union[Tuple[bool, str], Tuple[bool, dict]]:
    """
    Отправка приказа об изменении цен на сервер.
    """
    iiko_server = IikoServer()
    response = iiko_server.document(document)
    if response.status_code == 200:
        response = json.loads(response.text)
        if response['result'] == 'SUCCESS':
            return True, response
        return False, response
    return False, response.text
