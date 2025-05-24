CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    vendor VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL,
    in_stock INTEGER NOT NULL DEFAULT 0,
    min_stock INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    location VARCHAR(100) NOT NULL,
    image_url VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales_history (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    sale_date TIMESTAMP NOT NULL,
    price_at_sale FLOAT NOT NULL,
    CONSTRAINT fk_product
        FOREIGN KEY(product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_sales_history_product_id ON sales_history(product_id);
CREATE INDEX idx_sales_history_sale_date ON sales_history(sale_date);

INSERT INTO products (
    name, sku, category, vendor, price, 
    in_stock, min_stock, description, location
) VALUES 
(
    'Electronics Product 1', 
    'SKU4001', 
    'Electronics', 
    'VendorA', 
    20.00, 
    100, 
    10, 
    'Description for Electronics Product 1', 
    'Aisle 4'
),
(
    'Electronics Product 2', 
    'SKU4002', 
    'Electronics', 
    'VendorB', 
    25.00, 
    90, 
    15, 
    'Description for Electronics Product 2', 
    'Aisle 4'
),
(
    'Furniture Product 1', 
    'SKU5001', 
    'Furniture', 
    'VendorA', 
    22.50, 
    100, 
    10, 
    'Description for Furniture Product 1', 
    'Aisle 5'
),
(
    'Furniture Product 2', 
    'SKU5002', 
    'Furniture', 
    'VendorB', 
    27.50, 
    90, 
    15, 
    'Description for Furniture Product 2', 
    'Aisle 5'
);

INSERT INTO sales_history (
    product_id, quantity, sale_date, price_at_sale
) VALUES 
(1, 5, CURRENT_TIMESTAMP - INTERVAL '30 days', 20.00),
(1, 8, CURRENT_TIMESTAMP - INTERVAL '25 days', 20.00),
(1, 12, CURRENT_TIMESTAMP - INTERVAL '20 days', 19.99),
(1, 6, CURRENT_TIMESTAMP - INTERVAL '15 days', 19.99),
(2, 4, CURRENT_TIMESTAMP - INTERVAL '30 days', 25.00),
(2, 6, CURRENT_TIMESTAMP - INTERVAL '25 days', 25.00),
(2, 8, CURRENT_TIMESTAMP - INTERVAL '20 days', 24.99),
(3, 2, CURRENT_TIMESTAMP - INTERVAL '30 days', 22.50),
(3, 3, CURRENT_TIMESTAMP - INTERVAL '20 days', 22.50),
(3, 4, CURRENT_TIMESTAMP - INTERVAL '10 days', 22.99);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 