import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from app.models.product import Product
from app.models.product_in import ProductIn
from app.models.vendor import Vendor
from app.models.category import Category
from app.main import db, cache
from sqlalchemy.sql import func

class ForecastService:
    def __init__(self):
        self.scaler = StandardScaler()

    @cache.memoize(timeout=3600)
    def get_product_forecast(self, product_id):
        """Get forecast for a specific product"""
        product = Product.query.get_or_404(product_id)
        sales_data = self._get_sales_history(product_id)
        
        if sales_data.empty:
            return self._generate_default_forecast(product)
        
        forecast_data = self._calculate_forecast(product, sales_data)
        return self._format_forecast_response(product, forecast_data)

    def _get_sales_history(self, product_id):
        """Get sales history from ProductIn records"""
        sales = ProductIn.query.filter_by(prod_id=product_id).all()
        if not sales:
            return pd.DataFrame()
        
        df = pd.DataFrame([{
            'date': sale.createdAt,
            'quantity': sale.quantity,
            'price': sale.price_at_time,
            'vendor_id': sale.ven_id
        } for sale in sales])
        
        return df.set_index('date').sort_index()

    def _calculate_forecast(self, product, sales_data):
        """Calculate forecast metrics"""
        daily_avg = sales_data['quantity'].mean()
        daily_std = sales_data['quantity'].std()
        
        seasonal_factors = self._calculate_seasonality(sales_data, product.category.name if product.category else 'Unknown')
        price_elasticity = self._calculate_price_elasticity(sales_data)
        
        next_30_days = int(daily_avg * 30 * seasonal_factors['30_day'])
        next_90_days = int(daily_avg * 90 * seasonal_factors['90_day'])
        
        # Calculate stock levels from ProductIn
        current_stock = self._calculate_current_stock(product)
        daily_demand = daily_avg * seasonal_factors['30_day']
        days_remaining = int(current_stock / daily_demand) if daily_demand > 0 else 999
        
        suggested_order = max(0, int((daily_demand * 30) - current_stock))
        
        return {
            'next_30_days': next_30_days,
            'next_90_days': next_90_days,
            'days_remaining': days_remaining,
            'suggested_order_quantity': suggested_order,
            'confidence_score': self._calculate_confidence_score(sales_data)
        }

    def _calculate_current_stock(self, product):
        """Calculate current stock from ProductIn transactions"""
        total_in = db.session.query(
            func.sum(ProductIn.quantity)
        ).filter(
            ProductIn.prod_id == product.id
        ).scalar() or 0
        
        return total_in

    def _calculate_seasonality(self, sales_data, category):
        """Calculate seasonality factors based on historical data and category"""
        if sales_data.empty:
            return {'30_day': 1.0, '90_day': 1.0}
        
        current_month = datetime.now().month
        monthly_data = sales_data.resample('M').sum()
        
        if len(monthly_data) < 12:
            seasonal_factor = 1.0
        else:
            monthly_avg = monthly_data['quantity'].mean()
            current_month_avg = monthly_data[monthly_data.index.month == current_month]['quantity'].mean()
            seasonal_factor = current_month_avg / monthly_avg if monthly_avg > 0 else 1.0
        
        category_factors = {
            'Electronics': {'peak_months': [11, 12], 'factor': 1.3},
            'Clothing': {'peak_months': [3, 9], 'factor': 1.2},
            'Food': {'peak_months': range(1, 13), 'factor': 1.1}
        }
        
        category_adjustment = category_factors.get(category, {'peak_months': [], 'factor': 1.0})
        if current_month in category_adjustment['peak_months']:
            seasonal_factor *= category_adjustment['factor']
        
        return {
            '30_day': min(max(seasonal_factor, 0.5), 2.0),
            '90_day': min(max(seasonal_factor * 0.8, 0.6), 1.8)
        }

    def _calculate_price_elasticity(self, sales_data):
        """Calculate price elasticity of demand"""
        if len(sales_data) < 10:
            return -1.0
            
        price_changes = sales_data['price'].pct_change()
        quantity_changes = sales_data['quantity'].pct_change()
        
        mask = ~(np.isinf(price_changes) | np.isinf(quantity_changes))
        price_changes = price_changes[mask]
        quantity_changes = quantity_changes[mask]
        
        if len(price_changes) < 2:
            return -1.0
            
        elasticity = np.mean(quantity_changes / price_changes)
        return min(max(elasticity, -3.0), -0.1)

    def _calculate_confidence_score(self, sales_data):
        """Calculate confidence score for the forecast"""
        if sales_data.empty:
            return 0.3
            
        factors = {
            'data_points': min(len(sales_data) / 100, 0.4),
            'consistency': 0.3 * (1 - sales_data['quantity'].std() / sales_data['quantity'].mean()),
            'recency': 0.3 * (1 - (datetime.now() - sales_data.index.max()).days / 365)
        }
        
        confidence = sum(factors.values())
        return max(min(confidence, 1.0), 0.1)

    def _generate_default_forecast(self, product):
        """Generate default forecast for products with no history"""
        current_stock = self._calculate_current_stock(product)
        
        return {
            'product_id': product.id,
            'name': product.name,
            'category': product.category.name if product.category else None,
            'price': product.price,
            'current_stock': current_stock,
            'demand_forecast': {
                'next_30_days': 0,
                'next_90_days': 0
            },
            'stock_health': {
                'days_remaining': 999 if current_stock > 0 else 0,
                'suggested_order_quantity': 0
            },
            'vendor_info': self._get_vendor_info(product),
            'confidence_score': 0.3
        }

    def _format_forecast_response(self, product, forecast_data):
        """Format the forecast response with all necessary information"""
        current_stock = self._calculate_current_stock(product)
        
        return {
            'product_id': product.id,
            'name': product.name,
            'category': product.category.name if product.category else None,
            'price': product.price,
            'current_stock': current_stock,
            'demand_forecast': {
                'next_30_days': forecast_data['next_30_days'],
                'next_90_days': forecast_data['next_90_days']
            },
            'stock_health': {
                'days_remaining': forecast_data['days_remaining'],
                'suggested_order_quantity': forecast_data['suggested_order_quantity']
            },
            'vendor_info': self._get_vendor_info(product),
            'confidence_score': forecast_data['confidence_score']
        }

    def _get_vendor_info(self, product):
        """Get vendor information for a product"""
        latest_vendor = product.get_latest_vendor()
        if not latest_vendor:
            return {
                'name': 'Unknown',
                'lead_time_days': 7
            }
        
        # Calculate average lead time based on historical data
        lead_time = db.session.query(
            func.avg(
                func.extract('day', ProductIn.createdAt) - 
                func.extract('day', func.lag(ProductIn.createdAt).over(
                    order_by=ProductIn.createdAt
                ))
            )
        ).filter(
            ProductIn.ven_id == latest_vendor.id,
            ProductIn.prod_id == product.id
        ).scalar()

        return {
            'name': latest_vendor.name,
            'lead_time_days': int(lead_time) if lead_time else 7
        } 