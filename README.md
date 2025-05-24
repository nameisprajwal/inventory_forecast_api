# Inventory Demand Forecasting API

A Flask-based REST API for inventory demand forecasting that analyzes historical patterns and current inventory levels to predict future demand.

## Features

- Demand forecasting using multiple analytical methods
- Category-based seasonality analysis
- Price elasticity considerations
- Inventory alerts system
- Caching for performance optimization
- Comprehensive test coverage

## API Endpoints

### Forecast Endpoints

#### GET /api/forecast
Get forecasts for all products.

Response format:
```json
{
  "status": "success",
  "data": [
    {
      "product_id": 4,
      "name": "Electronics Product 1",
      "sku": "SKU4001",
      "category": "Electronics",
      "current_stock": 100,
      "min_stock": 10,
      "demand_forecast": {
        "next_30_days": 85,
        "next_90_days": 240
      },
      "stock_health": {
        "days_remaining": 30,
        "restock_urgent": false,
        "suggested_order_quantity": 50
      },
      "vendor_info": {
        "name": "VendorA",
        "lead_time_days": 7
      },
      "confidence_score": 0.85
    }
  ]
}
```

#### GET /api/forecast/<product_id>
Get detailed forecast for a specific product.

#### POST /api/forecast/calculate
Trigger forecast calculation for specific products.

Request body:
```json
{
  "product_ids": [1, 2, 3]
}
```

### Inventory Endpoints

#### GET /api/inventory/alert
Get products that need restocking (in_stock ≤ min_stock * 1.5).

Response format:
```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "product_id": 1,
      "name": "Electronics Product 1",
      "sku": "SKU4001",
      "category": "Electronics",
      "current_stock": 8,
      "min_stock": 10,
      "threshold": 15,
      "vendor": "VendorA",
      "location": "Aisle 4",
      "urgency": "HIGH"
    }
  ]
}
```

## Setup and Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd inventory_forecast_api
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The API will be available at http://localhost:5000

### Manual Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database and configure connection:
```bash
# Set your database URL environment variable
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/inventory_forecast"
```

4. Initialize the database and run migrations:
```bash
flask db init
flask db migrate
flask db upgrade
```

This will:
- Create the database tables
- Run the migration to populate the products table with initial data
- Set up necessary indexes

5. Run the application:
```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

## Development

### Database Management

The application uses SQLAlchemy with PostgreSQL. The database schema is managed using Flask-Migrate (Alembic).

#### Working with Migrations

Create a new migration:
```bash
flask db migrate -m "description of changes"
```

Apply migrations:
```bash
flask db upgrade
```

Rollback migrations:
```bash
flask db downgrade
```

### Running Tests

```bash
pytest
```

### Environment Variables

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_APP`: Set to "app"
- `FLASK_ENV`: "development" or "production"

Optional environment variables:
- `CACHE_TYPE`: Cache backend (default: "simple")
- `CACHE_DEFAULT_TIMEOUT`: Cache timeout in seconds (default: 300)

## Technical Details

### Forecasting Methods

The API uses multiple methods for demand forecasting:
- Moving average analysis
- Exponential smoothing
- Seasonality adjustments
- Price elasticity considerations

### Database Schema

#### Products Table
- id (int): Primary key
- name (str): Product name
- sku (str): Stock keeping unit
- category (str): Product category
- vendor (str): Supplier/vendor
- price (float): Current price
- in_stock (int): Current inventory count
- min_stock (int): Minimum required stock
- description (str): Product details
- location (str): Warehouse location
- image_url (str): Product image URL
- created_at (datetime): Record creation timestamp
- updated_at (datetime): Last update timestamp

#### Sales History Table
- id (int): Primary key
- product_id (int): Foreign key to products
- quantity (int): Quantity sold
- sale_date (datetime): Date of sale
- price_at_sale (float): Price at time of sale

## Performance Considerations

- API responses are cached for 5 minutes
- Forecasting calculations are memoized for 1 hour
- Database queries are optimized with proper indexing
- Batch processing for multiple products

## Error Handling

The API includes comprehensive error handling for:
- Missing products
- Invalid date ranges
- Negative stock values
- Database connection issues
- Calculation errors

## License

MIT License 

/api/forecast/
/api/forecast/1
/api/forecast/calculate
/api/inventory/alert