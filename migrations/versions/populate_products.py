"""populate products table

Revision ID: populate_products
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'populate_products'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create products table if it doesn't exist
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('sku', sa.String(50), unique=True, nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('vendor', sa.String(100), nullable=False),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('in_stock', sa.Integer, nullable=False),
        sa.Column('min_stock', sa.Integer, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('location', sa.String(100), nullable=False),
        sa.Column('image_url', sa.String(255)),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Set default timestamp for all records
    timestamp = datetime.utcnow()

    # Insert data from CSV
    products_data = [
        {'id': id, 'name': row['name'], 'sku': row['sku'], 'category': row['category'], 
         'vendor': row['vendor'], 'price': float(row['price']), 'in_stock': int(row['in_stock']), 
         'min_stock': int(row['min_stock']), 'description': row['description'], 
         'location': row['location'], 'image_url': None, 
         'created_at': timestamp, 'updated_at': timestamp}
        for id, row in enumerate([
            {'name': 'Electronics Product 1', 'sku': 'SKU4001', 'category': 'Electronics', 'vendor': 'VendorA', 'price': '20', 'in_stock': '100', 'min_stock': '10', 'description': 'Description for Electronics Product 1', 'location': 'Aisle 4'},
            {'name': 'Electronics Product 2', 'sku': 'SKU4002', 'category': 'Electronics', 'vendor': 'VendorB', 'price': '25', 'in_stock': '90', 'min_stock': '15', 'description': 'Description for Electronics Product 2', 'location': 'Aisle 4'},
            {'name': 'Electronics Product 3', 'sku': 'SKU4003', 'category': 'Electronics', 'vendor': 'VendorC', 'price': '30', 'in_stock': '80', 'min_stock': '20', 'description': 'Description for Electronics Product 3', 'location': 'Aisle 4'},
            {'name': 'Electronics Product 4', 'sku': 'SKU4004', 'category': 'Electronics', 'vendor': 'VendorD', 'price': '35', 'in_stock': '70', 'min_stock': '25', 'description': 'Description for Electronics Product 4', 'location': 'Aisle 4'},
            {'name': 'Furniture Product 1', 'sku': 'SKU5001', 'category': 'Furniture', 'vendor': 'VendorA', 'price': '22.5', 'in_stock': '100', 'min_stock': '10', 'description': 'Description for Furniture Product 1', 'location': 'Aisle 5'},
            {'name': 'Furniture Product 2', 'sku': 'SKU5002', 'category': 'Furniture', 'vendor': 'VendorB', 'price': '27.5', 'in_stock': '90', 'min_stock': '15', 'description': 'Description for Furniture Product 2', 'location': 'Aisle 5'},
            {'name': 'Furniture Product 3', 'sku': 'SKU5003', 'category': 'Furniture', 'vendor': 'VendorC', 'price': '32.5', 'in_stock': '80', 'min_stock': '20', 'description': 'Description for Furniture Product 3', 'location': 'Aisle 5'},
            {'name': 'Furniture Product 4', 'sku': 'SKU5004', 'category': 'Furniture', 'vendor': 'VendorD', 'price': '37.5', 'in_stock': '70', 'min_stock': '25', 'description': 'Description for Furniture Product 4', 'location': 'Aisle 5'},
            # Add all remaining products from the CSV file
        ], start=1)
    ]

    op.bulk_insert(sa.table('products',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.String(255)),
        sa.Column('sku', sa.String(50)),
        sa.Column('category', sa.String(100)),
        sa.Column('vendor', sa.String(100)),
        sa.Column('price', sa.Float),
        sa.Column('in_stock', sa.Integer),
        sa.Column('min_stock', sa.Integer),
        sa.Column('description', sa.Text),
        sa.Column('location', sa.String(100)),
        sa.Column('image_url', sa.String(255)),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime)
    ), products_data)

def downgrade():
    op.drop_table('products') 