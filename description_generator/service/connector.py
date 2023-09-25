from datetime import datetime, timedelta

from openpyxl import load_workbook

from service.dataclasses.document import DocumentData
from service.models import Product, Department


def from_xlsx_file_data_to_server_create_data(file):
    """
    Преобразование xlsx-файла в pydantic-класс.
    """
    document_data = {
        'date_incoming': str((datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d')),
        'status': 'NEW',
        'items': []
    }
    workbook = load_workbook(file)
    first_sheet = workbook.get_sheet_names()[0]
    worksheet = workbook.get_sheet_by_name(first_sheet)
    for row in worksheet.iter_rows(min_row=2):
        try:
            item = {
                'product_id': str(Product.objects.get(num=row[0].value).uuid),
                'price': row[2].value,
                'department_id': str(Department.objects.get(name=row[3].value).uuid)
            }
        except (Product.DoesNotExist, Department.DoesNotExist):
            return None
        document_data['items'].append(item)
    return DocumentData(**document_data)