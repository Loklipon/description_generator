from typing import Optional

from pydantic import BaseModel, Field


class ProductData(BaseModel):
    """
    Дата-класс элемента номенклатуры.
    """
    uuid: str = Field(alias='id')
    name: str
    description: Optional[str]
    type: Optional[str]
    num: Optional[str]
