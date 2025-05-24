from app.main import db
from datetime import datetime
from sqlalchemy import func

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    # Relationships
    category = db.relationship('Category', backref='products', lazy='select')
    product_ins = db.relationship('ProductIn', backref='product', lazy='select')

    def __repr__(self):
        return f'<Product {self.name}>'

    def get_latest_vendor(self):
        """Get the most recent vendor for this product"""
        latest_transaction = self.product_ins.order_by(ProductIn.createdAt.desc()).first()
        return latest_transaction.vendor if latest_transaction else None

    def get_sales_history(self, days=30):
        """Get sales history for forecasting"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        return db.session.query(
            ProductIn
        ).filter(
            ProductIn.prod_id == self.id,
            ProductIn.createdAt >= start_date
        ).order_by(ProductIn.createdAt.desc()).all()

    def get_daily_sales_avg(self, days=30):
        """Calculate average daily sales"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        result = db.session.query(
            func.avg(ProductIn.quantity).label('avg_daily_sales')
        ).filter(
            ProductIn.prod_id == self.id,
            ProductIn.createdAt >= start_date
        ).first()
        
        return result.avg_daily_sales if result.avg_daily_sales else 0

    def to_dict(self):
        latest_vendor = self.get_latest_vendor()
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category.name if self.category else None,
            'vendor': latest_vendor.name if latest_vendor else None
        } 