import hashlib
from typing import Union

import requests

from iiko.models import ServerLog
from service.dataclasses.document import DocumentData
from service.models import Product


class IikoServer:
    """
    iiko Server.
    """

    def __init__(self):
        self.login = 'admin'
        self.password = 'resto#test2'
        self.host = 'https://demostend-open-servis-71.iiko.it'
        self.port = '443'
        self.url = self.host + ':' + self.port
        self.params = {'key': self._auth()}

    def _auth(self) -> str:
        url = self.url + '/resto/api/auth'
        params = {
            'login': self.login,
            'pass': hashlib.sha1(self.password.encode('utf-8')).hexdigest()
        }
        response = requests.get(url, params=params)
        self._log(response, url=response.url, body=None)
        return response.text

    def _log(self, response, url, body) -> None:
        ServerLog.objects.create(
            url=url,
            request=body,
            response=response.text,
            response_status=response.status_code,
        )

    def logout(self) -> None:
        url = self.url + '/resto/api/logout'
        response = requests.get(url, params=self.params)
        self._log(response, url=response.url, body=None)

    def products_list(self, product: Union[Product, None]) -> requests.Response:
        url = self.url + '/resto/api/v2/entities/products/list'
        headers = {'Content-Type': 'application/json'}
        if product:
            params = self.params.copy()
            params['ids'] = str(product.uuid)
            response = requests.get(url, params=params, headers=headers)
            self._log(response, url=response.url, body=None)
        else:
            response = requests.get(url, params=self.params, headers=headers)
            self._log(response, url=response.url, body=None)
            self.logout()
        return response

    def chart(self, product: Product) -> requests.Response:
        url = self.url + '/resto/api/v2/assemblyCharts/getPrepared'
        headers = {'content-Type': 'application/json'}
        params = self.params.copy()
        params['date'] = '2023-09-14'
        params['productId'] = str(product.uuid)
        response = requests.get(url, params=params, headers=headers)
        self._log(response, url=response.url, body=None)
        return response

    def product_update(self, body: dict) -> requests.Response:
        url = self.url + '/resto/api/v2/entities/products/update'
        headers = {'content-Type': 'application/json'}
        params = self.params.copy()
        params['overrideFastCode'] = 'true'
        response = requests.post(url, data=body, params=params, headers=headers)
        self._log(response, response.url, body)
        return response

    def departments(self) -> requests.Response:
        url = self.url + '/resto/api/corporation/departments'
        headers = {'Content-Type': 'application/xml'}
        params = self.params.copy()
        response = requests.get(url, headers=headers, params=params)
        self._log(response, url=response.url, body=None)
        self.logout()
        return response

    def document(self, data: DocumentData) -> requests.Response:
        url = self.url + '/resto/api/v2/documents/menuChange'
        headers = {'Content-Type': 'application/json'}
        data = data.model_dump_json(by_alias=True)
        response = requests.post(url, data=data, params=self.params, headers=headers)
        self._log(response, url=response.url, body=data)
        self.logout()
        return response
