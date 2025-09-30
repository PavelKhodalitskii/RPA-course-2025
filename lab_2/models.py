from typing import Dict

from pydantic import BaseModel


class CarItem(BaseModel):
    name: str
    price: int
    amount: int

class CarItemsList(BaseModel):
    items: Dict[str, CarItem] = []