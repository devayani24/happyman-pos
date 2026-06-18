
-- Categories table (must come first — products references it)
CREATE TABLE IF NOT EXISTS categories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    type            TEXT NOT NULL,
    local_type_name TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Products table (references categories)
CREATE TABLE IF NOT EXISTS products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code    TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    local_name      TEXT NOT NULL,
    sold_by         TEXT NOT NULL,
    category_id     INTEGER NOT NULL,
    price           REAL NOT NULL,
    price_unit      REAL NOT NULL,
    price_unit_type TEXT NOT NULL,
    image           TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_code ON products(product_code);



CREATE TABLE IF NOT EXISTS sales (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_id             TEXT NOT NULL,
    bill_number         TEXT NOT NULL,
    timestamp           TEXT NOT NULL,
    total_price         REAL NOT NULL,
    payment_mode        TEXT NOT NULL,
    amount_received     REAL NOT NULL,
    amount_change       REAL,

    -- Refund/void support:
    transaction_type    TEXT NOT NULL DEFAULT 'sale',    -- 'sale' or 'refund'
    refund_for_bill     TEXT,                             -- bill# of original sale (NULL for sales)
    is_void             INTEGER NOT NULL DEFAULT 0,       -- 0=active, 1=voided
    void_reason         TEXT,                             -- why was it voided (entered by misatake, 0 for refund. (refund is recorded only in transaction_type))
    voided_at           TEXT,                             -- when was it voided
    
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sale_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id  INTEGER NOT NULL,
    product_id      TEXT NOT NULL,
    cart_unit       TEXT NOT NULL,
    cart_weight     REAL,
    cart_pieces     INTEGER,
    cart_packets    INTEGER NOT NULL,
    line_total      REAL NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (transaction_id) REFERENCES sales(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sales_timestamp ON sales(timestamp);
CREATE INDEX IF NOT EXISTS idx_sales_shop_id ON sales(shop_id);
CREATE INDEX IF NOT EXISTS idx_sale_items_transaction_id ON sale_items(transaction_id);