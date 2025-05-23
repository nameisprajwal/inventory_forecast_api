import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from app.models.product import Product
from app.models.sales_history import SalesHistory
from app import db, cache

class ForecastService:
    def __init__(self):
        self.scaler = StandardScaler()

    @cache.memoize(timeout=3600)
    def get_product_forecast(self, product_id):
        """
        Generate forecast for a specific product
        
        Args:
            product_id (int): Product ID to forecast
            
        Returns:
            dict: Forecast data including demand predictions and stock health
        """
        product = Product.query.get_or_404(product_id)
        sales_data = self._get_sales_history(product_id)
        
        if sales_data.empty:
            return self._generate_default_forecast(product)
        
        forecast_data = self._calculate_forecast(product, sales_data)
        return self._format_forecast_response(product, forecast_data)

    def _get_sales_history(self, product_id):
        """Retrieve and format sales history for analysis"""
        sales = SalesHistory.query.filter_by(product_id=product_id).all()
        if not sales:
            return pd.DataFrame()
        
        df = pd.DataFrame([{
            'date': sale.sale_date,
            'quantity': sale.quantity,
            'price': sale.price_at_sale
        } for sale in sales])
        
        return df.set_index('date').sort_index()

    def _calculate_forecast(self, product, sales_data):
        """
        Calculate demand forecast using multiple methods
        
        Args:
            product (Product): Product instance
            sales_data (DataFrame): Historical sales data
            
        Returns:
            dict: Forecast calculations
        """
        # Calculate basic metrics
        daily_avg = sales_data['quantity'].mean()
        daily_std = sales_data['quantity'].std()
        
        # Calculate seasonality factors
        seasonal_factors = self._calculate_seasonality(sales_data, product.category)
        
        # Calculate price elasticity
        price_elasticity = self._calculate_price_elasticity(sales_data)
        
        # Generate forecasts
        next_30_days = int(daily_avg * 30 * seasonal_factors['30_day'])
        next_90_days = int(daily_avg * 90 * seasonal_factors['90_day'])
        
        # Calculate stock health
        current_stock = product.in_stock
        daily_demand = daily_avg * seasonal_factors['30_day']
        days_remaining = int(current_stock / daily_demand) if daily_demand > 0 else 999
        
        # Calculate suggested order quantity
        buffer_stock = daily_std * 2  # 2 standard deviations for safety stock
        suggested_order = max(0, int((daily_demand * 30) - current_stock + buffer_stock))
        
        return {
            'next_30_days': next_30_days,
            'next_90_days': next_90_days,
            'days_remaining': days_remaining,
            'suggested_order_quantity': suggested_order,
            'confidence_score': self._calculate_confidence_score(sales_data)
        }

    def _calculate_seasonality(self, sales_data, category):
        """Calculate seasonality factors based on category and historical data"""
        if sales_data.empty:
            return {'30_day': 1.0, '90_day': 1.0}
        
        # Basic seasonality calculation
        current_month = datetime.now().month
        monthly_data = sales_data.resample('M').sum()
        
        if len(monthly_data) < 12:
            # Not enough data for proper seasonality
            seasonal_factor = 1.0
        else:
            # Calculate monthly seasonality factors
            monthly_avg = monthly_data['quantity'].mean()
            current_month_avg = monthly_data[monthly_data.index.month == current_month]['quantity'].mean()
            seasonal_factor = current_month_avg / monthly_avg if monthly_avg > 0 else 1.0
        
        # Adjust seasonality based on category
        category_factors = {
            'Electronics': {'peak_months': [11, 12], 'factor': 1.3},  # Holiday season
            'Clothing': {'peak_months': [3, 9], 'factor': 1.2},      # Season changes
            'Food': {'peak_months': range(1, 13), 'factor': 1.1}     # Steady demand
        }
        
        category_adjustment = category_factors.get(category, {'peak_months': [], 'factor': 1.0})
        if current_month in category_adjustment['peak_months']:
            seasonal_factor *= category_adjustment['factor']
        
        return {
            '30_day': min(max(seasonal_factor, 0.5), 2.0),  # Limit factor between 0.5 and 2.0
            '90_day': min(max(seasonal_factor * 0.8, 0.6), 1.8)  # Slightly moderate for longer term
        }

    def _calculate_price_elasticity(self, sales_data):
        """Calculate price elasticity of demand"""
        if len(sales_data) < 10:  # Need sufficient data points
            return -1.0  # Default elasticity
            
        price_changes = sales_data['price'].pct_change()
        quantity_changes = sales_data['quantity'].pct_change()
        
        # Remove infinite values and outliers
        mask = ~(np.isinf(price_changes) | np.isinf(quantity_changes))
        price_changes = price_changes[mask]
        quantity_changes = quantity_changes[mask]
        
        if len(price_changes) < 2:
            return -1.0
            
        # Calculate elasticity as percentage change in quantity / percentage change in price
        elasticity = np.mean(quantity_changes / price_changes)
        return min(max(elasticity, -3.0), -0.1)  # Limit between -3.0 and -0.1

    def _calculate_confidence_score(self, sales_data):
        """Calculate confidence score for the forecast"""
        if sales_data.empty:
            return 0.3  # Low confidence for no data
            
        factors = {
            'data_points': min(len(sales_data) / 100, 0.4),  # Up to 40% based on amount of data
            'consistency': 0.3 * (1 - sales_data['quantity'].std() / sales_data['quantity'].mean()),
            'recency': 0.3 * (1 - (datetime.now() - sales_data.index.max()).days / 365)
        }
        
        confidence = sum(factors.values())
        return max(min(confidence, 1.0), 0.1)  # Ensure between 0.1 and 1.0

    def _generate_default_forecast(self, product):
        """Generate a default forecast when no historical data is available"""
        return {
            'product_id': product.id,
            'name': product.name,
            'sku': product.sku,
            'category': product.category,
            'current_stock': product.in_stock,
            'min_stock': product.min_stock,
            'demand_forecast': {
                'next_30_days': product.min_stock * 2,  # Conservative estimate
                'next_90_days': product.min_stock * 6
            },
            'stock_health': {
                'days_remaining': 30 if product.in_stock > 0 else 0,
                'restock_urgent': product.needs_restock(),
                'suggested_order_quantity': product.min_stock
            },
            'vendor_info': {
                'name': product.vendor,
                'lead_time_days': 7  # Default lead time
            },
            'confidence_score': 0.3  # Low confidence for default forecast
        }

    def _format_forecast_response(self, product, forecast_data):
        """Format the forecast data into the required response structure"""
        return {
            'product_id': product.id,
            'name': product.name,
            'sku': product.sku,
            'category': product.category,
            'current_stock': product.in_stock,
            'min_stock': product.min_stock,
            'demand_forecast': {
                'next_30_days': forecast_data['next_30_days'],
                'next_90_days': forecast_data['next_90_days']
            },
            'stock_health': {
                'days_remaining': forecast_data['days_remaining'],
                'restock_urgent': product.needs_restock(),
                'suggested_order_quantity': forecast_data['suggested_order_quantity']
            },
            'vendor_info': {
                'name': product.vendor,
                'lead_time_days': 7  # This could be enhanced with vendor-specific data
            },
            'confidence_score': forecast_data['confidence_score']
        } 