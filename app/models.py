from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import Literal


class TransactionItem(BaseModel):
    product_id: str
    cart_unit: Literal['g', 'kg', 'pc']
    cart_weight: Optional[float] = None
    cart_pieces: Optional[int] = None
    cart_packets: int
    line_total: float


class Transaction(BaseModel):
    shop_id: str
    # bill_number: str
    timestamp: datetime
    total_price: float
    payment_mode: Literal['cash', 'gpay']
    amount_received: float
    amount_change: float
    
    # New fields-later when refund UI is developed:
    
    
    items: list[TransactionItem]

class CategorySeed(BaseModel):
    """Schema for a single category in seed_data.json"""
    type: str
    local_type_name: str


class ProductSeed(BaseModel):
    """Schema for a single product in seed_data.json"""
    product_code: str
    name: str
    local_name: str
    category_type: str
    sold_by: Literal['weight', 'pieces']
    price: float
    price_unit: float
    price_unit_type: Literal['kg', 'pc']
    image: Optional[str] = None
    is_active: bool = True


class SeedData(BaseModel):
    """The full seed_data.json schema"""
    categories: list[CategorySeed]
    products: list[ProductSeed]