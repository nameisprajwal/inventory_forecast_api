from flask import Blueprint, jsonify, request
from app.services.forecast_service import ForecastService
from app.models.product import Product
from app.main import cache, db

forecast_bp = Blueprint('forecast', __name__)
forecast_service = ForecastService()

@forecast_bp.route('/', methods=['GET'])
@cache.cached(timeout=300)
def get_all_forecasts():
    """Get forecasts for all products"""
    try:
        products = Product.query.all()
        forecasts = []
        
        for product in products:
            forecast = forecast_service.get_product_forecast(product.id)
            forecasts.append(forecast)
        
        return jsonify({
            'status': 'success',
            'data': forecasts
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@forecast_bp.route('/<int:product_id>', methods=['GET'])
def get_product_forecast(product_id):
    """Get detailed forecast for a specific product"""
    try:
        forecast = forecast_service.get_product_forecast(product_id)
        return jsonify({
            'status': 'success',
            'data': forecast
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404 if 'not found' in str(e).lower() else 500

@forecast_bp.route('/calculate', methods=['POST'])
def calculate_forecast():
    """Trigger forecast calculation for specific products or all products"""
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', []) if data else []
        
        if not product_ids:
            # Calculate for all products
            products = Product.query.all()
            product_ids = [p.id for p in products]
        
        forecasts = []
        for product_id in product_ids:
            # Clear cache for this product
            cache.delete_memoized(forecast_service.get_product_forecast, product_id)
            # Calculate new forecast
            forecast = forecast_service.get_product_forecast(product_id)
            forecasts.append(forecast)
        
        return jsonify({
            'status': 'success',
            'message': f'Calculated forecasts for {len(forecasts)} products',
            'data': forecasts
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 