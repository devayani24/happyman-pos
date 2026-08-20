from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import FileResponse
from app.models import Transaction
from app.db.database import save_sale_to_db, get_all_categories, get_all_products,get_sales_data,get_items_for_sale,void_sale
from app.sales_report import generate_report
from fastapi.staticfiles import StaticFiles              
from pathlib import Path                                
import sys 

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
def show_sales(period: str = "today"):
    return get_sales_data(period = period)

@app.get('/api/sales/{bill_number}/items')
def get_sale_items(bill_number: int):
    """Return items for a specific sale."""
    return get_items_for_sale(bill_number)

@app.post("/api/sales/{bill_number}/{selected_reason}/void")
def void_sale_endpoint(bill_number: int, selected_reason: str):
    
    status = void_sale(bill_number, selected_reason)
    return status

# ============================================================
# STATIC FILES 
# ============================================================

def get_frontend_dir():
    """
    Get the frontend directory.
    - Bundled: from PyInstaller temp folder
    - Dev: from project structure
    """
    if getattr(sys, 'frozen', False):
        path = Path(sys._MEIPASS) / "app" / "frontend"
    else:
        path = Path(__file__).parent / "frontend"
    print(f"Frontend directory: {path}")
    print(f"Exists: {path.exists()}")
    return path


# Serve frontend at root - catches all URLs not matched by API routes above
app.mount(
    "/", 
    StaticFiles(directory=str(get_frontend_dir()), html=True), 
    name="frontend"
)
