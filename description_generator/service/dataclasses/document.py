from typing import Optional

from pydantic import BaseModel, Field


class ItemData(BaseModel):
    """
    Дата-класс продукта с изменяемой ценой.
    """
    department_id: str = Field(alias='departmentId')
    product_id: str = Field(alias='productId')
    price: float
    dish_of_day: bool = Field(alias='dishOfDay')
    including: bool = Field
    flyer_program: bool = Field(alias='flyerProgram')
    num: int
    product_size_id: Optional[str] = Field(alias='productSizeId')

    class Config:
        populate_by_name = True


class DocumentData(BaseModel):
    """
    Дата-класс приказа на изменение цен.
    """
    date_incoming: str = Field(alias='dateIncoming')
    status: str
    items: list[ItemData]
    short_name: str = Field(alias='shortName')
    delete_previous_menu: bool = Field(alias='deletePreviousMenu')

    class Config:
        populate_by_name = True
