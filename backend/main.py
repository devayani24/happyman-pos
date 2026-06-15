from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from models import Transaction

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
    
    
    print(sale)
    
    
    return sale
