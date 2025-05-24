from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_caching import Cache
from flask_cors import CORS
from datetime import timedelta
import os

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://Scott:Tiger12345@database-1.cfcoiu6cowe0.ap-south-1.rds.amazonaws.com:5432/postgres')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    # Enable CORS for all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    
    from app.api.forecast import forecast_bp
    from app.api.inventory import inventory_bp
    
    app.register_blueprint(forecast_bp, url_prefix='/api/forecast')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app() 