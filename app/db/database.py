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

def save_sale(transaction: Transaction):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
      cursor.execute(
        """ INSERT INTO sales (shop_id,bill_number,timestamp,total_price,payment_mode,amount_received,amount_change) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (transaction.shop_id, transaction.bill_number,transaction.timestamp, transaction.total_price,transaction.payment_mode, transaction.amount_received,transaction.amount_change)
      )
      sale_id = cursor.lastrowid

      for item in transaction.items:
         cursor.execute(
            '''INSERT INTO sale_items 
              (transaction_id, product_id, cart_unit, cart_weight,cart_pieces, cart_packets, line_total)
              VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (sale_id, item.product_id, item.cart_unit, item.cart_weight,item.cart_pieces, item.cart_packets, item.line_total)
         )
      
      conn.commit()
      return sale_id
   
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()