from pydantic import BaseModel, Field


class ItemData(BaseModel):
    """
    Дата-класс продукта с изменяемой ценой.
    """
    department_id: str = Field(alias='departmentId')
    product_id: str = Field(alias='productId')
    price: float

    class Config:
        populate_by_name = True


class DocumentData(BaseModel):
    """
    Дата-класс приказа на изменение цен.
    """
    date_incoming: str = Field(alias='dateIncoming')
    status: str
    items: list[ItemData]

    class Config:
        populate_by_name = True
