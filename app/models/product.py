from app.main import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    vendor = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Integer, nullable=False, default=0)
    min_stock = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)
    location = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    sales_history = db.relationship('SalesHistory', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'

    def needs_restock(self):
        return self.in_stock <= (self.min_stock * 1.5)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'category': self.category,
            'vendor': self.vendor,
            'price': self.price,
            'in_stock': self.in_stock,
            'min_stock': self.min_stock,
            'description': self.description,
            'location': self.location,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 