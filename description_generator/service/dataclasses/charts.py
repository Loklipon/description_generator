from typing import Union

from pydantic import BaseModel, Field


class ItemData(BaseModel):
    """
    Дата-класс элемента номенклатуры,
    входящего в состав ТТК.
    """
    uuid: str = Field(alias='productId')


class PreparedChartData(BaseModel):
    """
    Дата-класс списка элементов номенклатуры,
    входящих в состав ТТК.
    """
    items: list[ItemData]


class ResponseData(BaseModel):
    """
    Дата-класс списка ТТК.
    """
    prepared_charts: list[Union[PreparedChartData, None]] = Field(alias='preparedCharts')
