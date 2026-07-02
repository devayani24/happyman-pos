import sqlite3
from pathlib import Path
from contextlib import contextmanager
from app.config import DATABASE_PATH
from app.models import Transaction


@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    # rows accessible by column name
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_sales_data():
    """Return all sales with their item counts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.*,
                COUNT(si.id) AS items_count
            FROM sales s
            LEFT JOIN sale_items si ON si.transaction_id = s.id
            GROUP BY s.id
            ORDER BY s.id ASC
        """)
        return [dict(row) for row in cursor.fetchall()]
   
def get_sale_items_data():
   with get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute(
        """
        SELECT 
            s.bill_number,
            s.is_void,
            p.name,
            p.local_name,
            COALESCE(si.cart_weight, si.cart_pieces) AS quantity,
            si.cart_unit AS unit,
            si.cart_packets AS packets,
            si.line_total
        FROM sale_items si
        LEFT JOIN sales s ON s.id = si.transaction_id
        LEFT JOIN products p ON p.product_code = si.product_id
        ORDER BY s.bill_number, p.name
        """
       )
       return [ dict(row) for row in cursor.fetchall()]

def save_sale_to_db(sale: Transaction):
    
    with get_connection() as conn:
      cursor = conn.cursor()
      # get the last bill number from the server
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

      # save sale to the database
      cursor.execute(
        """ INSERT INTO sales (shop_id,bill_number,timestamp,total_price,payment_mode,amount_received,amount_change) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (sale.shop_id, new_bill_number,sale.timestamp.isoformat(), sale.total_price,sale.payment_mode, sale.amount_received,sale.amount_change)
      )
      # get the last sale id from the database
      sale_id = cursor.lastrowid

      for item in sale.items:
        cursor.execute(
            '''INSERT INTO sale_items 
              (transaction_id, product_id, cart_unit, cart_weight,cart_pieces, cart_packets, line_total)
              VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (sale_id, item.product_id, item.cart_unit, item.cart_weight,item.cart_pieces, item.cart_packets, item.line_total)
        )
      return new_bill_number


def get_all_categories():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories")

        # Convert rows to dicts with camelCase keys for JS
        categories = [
            {
                'id': row['id'],
                'code': row['code'],
                'type': row['type'],
                'localTypeName': row['local_type_name']
            }
            for row in cursor.fetchall()
        ]
        print(categories)
        
        return categories
    
def get_all_products():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.product_code AS id,
                p.name,
                p.local_name AS localName,
                p.category_id AS categoryId,
                p.sold_by AS soldBy,
                p.price,
                p.price_unit AS priceUnit,
                p.price_unit_type AS priceUnitType,
                p.image,
                p.is_active AS isActive
            FROM products p
            WHERE p.is_active = 1
            ORDER BY p.category_id, p.product_code
        """)
        products = [dict(row) for row in cursor.fetchall()]
        print(len(products))
        return products

def get_metrics():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                sum(total_price) AS total_revenue, 
                count(id)AS sale_count, 
                avg(total_price)AS avg_revenue,
                sum(CASE WHEN payment_mode = 'cash' THEN total_price ELSE 0 END) AS cash_total,
                sum(CASE WHEN payment_mode = 'gpay' THEN total_price ELSE 0 END) AS gpay_total
            FROM sales
            """
        )
        metrics = dict(cursor.fetchone())
        return metrics

def get_product_metrics():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.name, count(si.product_id) as product_count, sum(si.line_total) as revenue 
            FROM sale_items si
            JOIN products p on p.product_code = si.product_id
            GROUP BY product_id
            ORDER BY product_count DESC
            """
        )
        product_metrics = [dict(row) for row in cursor.fetchall()]
        return product_metrics

if __name__ == "__main__":
    get_all_products()