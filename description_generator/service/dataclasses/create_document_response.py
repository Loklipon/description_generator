from pydantic import BaseModel, Field


class Item(BaseModel):
    """
    Дата-класс единицы номенклатуры.
    """
    num: int
    uuid: str = Field(alias='productId')


class InternalFieldResponse(BaseModel):
    """
    Дата-класс поля response.
    """
    items: list[Item]
    document_number: str = Field(default=None, alias='documentNumber')


class Error(BaseModel):
    """
    Дата-класс ошибки.
    """
    value: str


class Response(BaseModel):
    """
    Дата-класс ответа на создание приказа.
    """
    result: str
    errors: list[Error]
    response: InternalFieldResponse
