import os
import sys
from flask import Flask, jsonify
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

from extensions import db, jwt, cors
from config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.admin import admin_bp
    from routes.bundles import bundles_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(bundles_bp)

    # Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    # Create tables and seed admin
    with app.app_context():
        db.create_all()   # creates all tables first
        _seed_admin()     # then seeds admin user

    return app


def _seed_admin():
    """Ensure the admin user exists on startup with the correct password hash."""
    from models.user import User

    admin = User.query.filter_by(email='admin@bushido.com').first()
    if admin:
        admin.password_hash = generate_password_hash('bushido2026')
    else:
        admin = User(
            username='admin',
            email='admin@bushido.com',
            password_hash=generate_password_hash('bushido2026'),
            role='admin',
        )
        db.session.add(admin)

    db.session.commit()
    print('✅ Admin user ready: admin@bushido.com / bushido2026', file=sys.stderr)


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
