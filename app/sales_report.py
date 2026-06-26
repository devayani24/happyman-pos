from openpyxl import Workbook
from app.config import REPORT_DIR, SHOP_ID
from datetime import datetime

def sales_report():
  timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  filename = f"HappyMan_{SHOP_ID}_{timestamp}.xlsx"
  report_path = REPORT_DIR / filename
  
  wb = Workbook()
  ws = wb.active

  ws.title = "Hello World"

  wb.save(report_path)



if __name__ == "__main__":
    sales_report()

