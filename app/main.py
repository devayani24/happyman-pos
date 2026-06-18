from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.models import Transaction
from app.db.database import save_sale_to_db

app = FastAPI()

# ← add this middleware right after creating the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow any origin (fine for dev)
    allow_credentials=True,
    allow_methods=["*"],           # allow any HTTP method
    allow_headers=["*"],           # allow any headers
)

@app.post('/save-sale')
def save_sale(sale: Transaction):
    
    save_sale_to_db(sale)
    print(sale)
    
    
    # return {"status": "ok", "bill_number": sale.bill_number}
