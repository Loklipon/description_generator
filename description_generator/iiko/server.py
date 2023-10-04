import hashlib
from typing import Union

import requests
from django.utils import timezone as tz

from iiko.models import ServerLog
from service.dataclasses.create_document_request import DocumentData
from service.models import Product, Chain


class IikoServer:
    """
    iiko Server.
    """

    def __init__(self, org: Chain):
        self.login = org.server_login
        self.password = org.server_password
        self.host = org.server_url
        self.port = org.server_port
        self.url = self.host + ':' + self.port
        self.params = {'key': self._auth()}

    def _auth(self) -> str:
        method_url = '/resto/api/auth'
        url = self.url + method_url
        params = {
            'login': self.login,
            'pass': hashlib.sha1(self.password.encode('utf-8')).hexdigest()
        }
        response = requests.get(url, params=params)
        self._log(response, url=method_url, body=None)
        return response.text

    def _log(self, response, url, body) -> None:
        ServerLog.objects.create(
            url=url,
            request=body,
            response=response.text,
            response_status=response.status_code,
        )

    def logout(self) -> None:
        method_url = '/resto/api/logout'
        url = self.url + method_url
        response = requests.get(url, params=self.params)
        self._log(response, url=method_url, body=None)

    def products_list(self, product: Union[Product, None]) -> requests.Response:
        method_url = '/resto/api/v2/entities/products/list'
        url = self.url + method_url
        headers = {'Content-Type': 'application/json'}
        params = self.params.copy()
        if product:
            params.update({
                'ids': str(product.uuid)
            })
            response = requests.get(url, params=params, headers=headers)
            self._log(response, url=method_url, body=None)
        else:
            response = requests.get(url, params=self.params, headers=headers)
            self._log(response, url=method_url, body=None)
            self.logout()
        return response

    def chart(self, product: Product) -> requests.Response:
        method_url = '/resto/api/v2/assemblyCharts/getPrepared'
        url = self.url + method_url
        headers = {'Content-Type': 'application/json'}
        params = self.params.copy()
        params.update({
            'date': tz.now().strftime('%Y-%m-%d'),
            'productId': str(product.uuid)
        })
        response = requests.get(url, params=params, headers=headers)
        self._log(response, url=method_url, body=None)
        return response

    def product_update(self, body: str) -> requests.Response:
        method_url = '/resto/api/v2/entities/products/update'
        url = self.url + method_url
        headers = {'Content-Type': 'application/json'}
        params = self.params.copy()
        params['overrideFastCode'] = 'true'
        response = requests.post(url, data=body, params=params, headers=headers)
        self._log(response, url=method_url, body=body)
        return response

    def departments(self) -> requests.Response:
        method_url = '/resto/api/corporation/departments'
        url = self.url + method_url
        headers = {'Content-Type': 'application/xml'}
        params = self.params.copy()
        response = requests.get(url, headers=headers, params=params)
        self._log(response, url=method_url, body=None)
        self.logout()
        return response

    def document(self, data: DocumentData) -> requests.Response:
        method_url = '/resto/api/v2/documents/menuChange'
        url = self.url + method_url
        headers = {'Content-Type': 'application/json'}
        data = data.model_dump_json(by_alias=True)
        response = requests.post(url, data=data, params=self.params, headers=headers)
        self._log(response, url=method_url, body=data)
        self.logout()
        return response
