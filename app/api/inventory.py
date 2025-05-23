from flask import Blueprint, jsonify
from app.models.product import Product
from app.main import cache, db

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/alert', methods=['GET'])
@cache.cached(timeout=300)
def get_inventory_alerts():
    """Get products that need restocking"""
    try:
        products = Product.query.all()
        alerts = []
        
        for product in products:
            if product.needs_restock():
                alerts.append({
                    'product_id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'category': product.category,
                    'current_stock': product.in_stock,
                    'min_stock': product.min_stock,
                    'threshold': product.min_stock * 1.5,
                    'vendor': product.vendor,
                    'location': product.location,
                    'price': product.price,
                    'description': product.description,
                    'image_url': product.image_url,
                    'urgency': 'HIGH' if product.in_stock <= product.min_stock else 'MEDIUM'
                })
        
        return jsonify({
            'status': 'success',
            'count': len(alerts),
            'data': alerts
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 