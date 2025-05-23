from app.main import db
from datetime import datetime

class SalesHistory(db.Model):
    __tablename__ = 'sales_history'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price_at_sale = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<SalesHistory {self.product_id} - {self.sale_date}>'

    def to_dict(self):
        """Convert sales history to dictionary format"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'sale_date': self.sale_date.isoformat(),
            'price_at_sale': self.price_at_sale,
            'created_at': self.created_at.isoformat()
        } 