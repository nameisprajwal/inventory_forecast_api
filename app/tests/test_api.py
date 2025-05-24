import pytest
from datetime import datetime, timedelta
from app.main import create_app, db
from app.models.product import Product
from app.models.product_in import ProductIn
from app.models.category import Category
from app.models.vendor import Vendor

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
    # Create test category
    category = Category(name='Electronics')
    db.session.add(category)
    
    # Create test vendor
    vendor = Vendor(name='VendorA')
    db.session.add(vendor)
    db.session.commit()
    
    # Create test product
    product = Product(
        name='Electronics Product 1',
        price=99.99,
        cat_id=category.id
    )
    db.session.add(product)
    db.session.commit()
    
    # Create product transactions
    dates = [(datetime.now() - timedelta(days=x)) for x in range(30)]
    for date in dates:
        transaction = ProductIn(
            prod_id=product.id,
            ven_id=vendor.id,
            quantity=5,
            createdAt=date,
            price_at_time=99.99
        )
        db.session.add(transaction)
    
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
    # Add more transactions to trigger alert
    with client.application.app_context():
        product = Product.query.get(1)
        vendor = Vendor.query.first()
        
        # Add some outgoing transactions
        for _ in range(5):
            transaction = ProductIn(
                prod_id=product.id,
                ven_id=vendor.id,
                quantity=-10,  # Negative quantity for outgoing
                createdAt=datetime.utcnow(),
                price_at_time=product.price
            )
            db.session.add(transaction)
        db.session.commit()
    
    response = client.get('/api/inventory/alert')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) > 0
    
    alert = data['data'][0]
    assert alert['product_id'] == 1
    assert 'urgency' in alert

def test_invalid_product_forecast(client):
    """Test getting forecast for non-existent product"""
    response = client.get('/api/forecast/999')
    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'error' 