from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import FileResponse
from app.models import Transaction
from app.db.database import save_sale_to_db, get_all_categories, get_all_products,get_sales_data
from app.sales_report import generate_report

app = FastAPI()

# ← add this middleware right after creating the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow any origin (fine for dev)
    allow_credentials=True,
    allow_methods=["*"],           # allow any HTTP method
    allow_headers=["*"],           # allow any headers
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

bill_number = ''
@app.post('/save-sale')
def save_sale(sale: Transaction):
    
    bill_number = save_sale_to_db(sale)
    print(bill_number)
    
    
    return {"status": "ok", "bill_number": bill_number}

@app.get('/categories')
def fetch_categories():
    return get_all_categories()

@app.get('/products')
def fetch_products():
    return get_all_products()

@app.get("/api/export-report")
async def export_report():
    report_path = generate_report()
    return FileResponse(
        path=report_path,
        filename=report_path.name,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.get('/api/show-sales')
def show_sales():
    return get_sales_data(period = "today")

