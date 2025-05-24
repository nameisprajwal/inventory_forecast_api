from flask import Blueprint, jsonify
from app.models.product import Product
from app.main import cache, db
from app.models.product_in import ProductIn
from datetime import datetime, timedelta
from sqlalchemy import func

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/alert', methods=['GET'])
@cache.cached(timeout=300)
def get_inventory_alerts():
    try:
        products = Product.query.all()
        alerts = []
        
        for product in products:
            # Calculate current stock from ProductIn
            current_stock = db.session.query(
                func.sum(ProductIn.quantity)
            ).filter(
                ProductIn.prod_id == product.id
            ).scalar() or 0
            
            # Get average daily demand
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            daily_demand = db.session.query(
                func.avg(ProductIn.quantity)
            ).filter(
                ProductIn.prod_id == product.id,
                ProductIn.createdAt >= thirty_days_ago
            ).scalar() or 0
            
            # Alert if less than 30 days of stock remaining
            if current_stock <= (daily_demand * 30):
                latest_transaction = product.product_ins.order_by(ProductIn.createdAt.desc()).first()
                vendor_name = latest_transaction.vendor.name if latest_transaction else "Unknown"
                
                alerts.append({
                    'product_id': product.id,
                    'name': product.name,
                    'category': product.category.name if product.category else None,
                    'current_stock': current_stock,
                    'daily_demand': daily_demand,
                    'days_remaining': int(current_stock / daily_demand) if daily_demand > 0 else 999,
                    'vendor': vendor_name,
                    'price': product.price,
                    'urgency': 'HIGH' if current_stock <= (daily_demand * 7) else 'MEDIUM'
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