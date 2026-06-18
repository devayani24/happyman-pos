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
    bill_number: str
    timestamp: datetime
    total_price: float
    payment_mode: Literal['cash', 'gpay']
    amount_received: float
    amount_change: float
    
    # New fields-later when refund UI is developed:
    
    
    items: list[TransactionItem]