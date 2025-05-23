import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.product import Product
from app.models.sales_history import SalesHistory

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        _create_test_data()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def _create_test_data():
    """Create sample data for testing"""
    # Create test product
    product = Product(
        name='Electronics Product 1',
        sku='SKU4001',
        category='Electronics',
        vendor='VendorA',
        price=99.99,
        in_stock=100,
        min_stock=10,
        description='Test product',
        location='Aisle 4'
    )
    db.session.add(product)
    db.session.commit()
    
    # Create sales history
    dates = [(datetime.now() - timedelta(days=x)) for x in range(30)]
    for date in dates:
        sale = SalesHistory(
            product_id=product.id,
            quantity=5,
            sale_date=date,
            price_at_sale=99.99
        )
        db.session.add(sale)
    
    db.session.commit()

def test_get_all_forecasts(client):
    """Test getting forecasts for all products"""
    response = client.get('/api/forecast/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) > 0
    
    forecast = data['data'][0]
    assert 'product_id' in forecast
    assert 'demand_forecast' in forecast
    assert 'stock_health' in forecast

def test_get_product_forecast(client):
    """Test getting forecast for a specific product"""
    response = client.get('/api/forecast/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    
    forecast = data['data']
    assert forecast['product_id'] == 1
    assert forecast['name'] == 'Electronics Product 1'
    assert 'demand_forecast' in forecast
    assert 'next_30_days' in forecast['demand_forecast']
    assert 'next_90_days' in forecast['demand_forecast']

def test_calculate_forecast(client):
    """Test calculating forecasts"""
    response = client.post('/api/forecast/calculate', 
                         json={'product_ids': [1]})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) == 1

def test_get_inventory_alerts(client):
    """Test getting inventory alerts"""
    # First update product to trigger alert
    with client.application.app_context():
        product = Product.query.get(1)
        product.in_stock = 5  # Below min_stock
        db.session.commit()
    
    response = client.get('/api/inventory/alert')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) > 0
    
    alert = data['data'][0]
    assert alert['product_id'] == 1
    assert alert['urgency'] == 'HIGH'

def test_invalid_product_forecast(client):
    """Test getting forecast for non-existent product"""
    response = client.get('/api/forecast/999')
    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'error' 