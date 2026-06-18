import sqlite3
from pathlib import Path
from app.config import DATABASE_PATH
from app.models import Transaction


def init_db():
  schema_path = Path(__file__).parent/"schema.sql"
  schema_sql = schema_path.read_text()

  conn = sqlite3.connect(DATABASE_PATH)

  try:
    conn.executescript(schema_sql)
    conn.commit()
    print(f"✓ Database initialized at {DATABASE_PATH}")
  
  except Exception as e:
        conn.rollback()
        raise
  
  finally:
        conn.close()

def save_sale_to_db(sale: Transaction):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:

      # get the last sale id from the database
      cursor.execute(
          """ 
          SELECT bill_number FROM sales
          WHERE shop_id = ?
          ORDER BY id DESC LIMIT 1;
          
          """,(sale.shop_id,))
      
      last_row_bill_number =  cursor.fetchone()
      if last_row_bill_number:
          last_number  = int(last_row_bill_number[0].split("-")[1])
          new_number = last_number + 1
      else:
          new_number = 1

      new_bill_number = f"{sale.shop_id}-{new_number}"

      cursor.execute(
        """ INSERT INTO sales (shop_id,bill_number,timestamp,total_price,payment_mode,amount_received,amount_change) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (sale.shop_id, new_bill_number,sale.timestamp.isoformat(), sale.total_price,sale.payment_mode, sale.amount_received,sale.amount_change)
      )
      sale_id = cursor.lastrowid

      for item in sale.items:
         cursor.execute(
            '''INSERT INTO sale_items 
              (transaction_id, product_id, cart_unit, cart_weight,cart_pieces, cart_packets, line_total)
              VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (sale_id, item.product_id, item.cart_unit, item.cart_weight,item.cart_pieces, item.cart_packets, item.line_total)
         )
      
      conn.commit()
      return new_bill_number
   
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()