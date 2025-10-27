from flask import Flask, session
from applications.database import db
from applications.config import Config
from applications.model import *
from flask_restful import Api, Resource
from werkzeug.security import generate_password_hash
from pyngrok import ngrok  # ✅ Use Ngrok for public access
import os

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Load Configuration
    app.config.from_object(Config)

    # Initialize Flask-RESTful API
    api = Api(app)

    # Initialize Database
    db.init_app(app)

    # Database and Role Setup
    with app.app_context():
        db.create_all()

        # Define roles
        roles = ['admin', 'customer', 'professional']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name))

        # Placeholder Admin Account
        admin_email = 'admin@example.com'
        admin_password = 'admin_password'

        if not User.query.filter_by(email=admin_email).first():
            admin_role = Role.query.filter_by(name='admin').first()
            admin_user = User(
                username='Admin',
                email=admin_email,
                password=generate_password_hash(admin_password),  # Secure password storage
                roles=[admin_role],
                approved=True
            )
            db.session.add(admin_user)

        db.session.commit()

    return app, api

# Initialize App and API
app, api = create_app()

# Make sessions permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Import Routes
from applications.routes import *

# Example RESTful API Endpoint
class ServiceAPI(Resource):
    def get(self):
        try:
            services = Services.query.all()
            response = [{'id': service.id, 'name': service.service_name, 'price': service.price} for service in services]
            return {'status': 'success', 'data': response}, 200
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500

# Register RESTful API Resource
api.add_resource(ServiceAPI, '/api/services')

# ✅ Start Flask App & a Single Ngrok Tunnel (Allowing Everyone)
if __name__ == '__main__':
    port = 5000  # ✅ Use only one port for a single tunnel

    # ✅ Kill any old Ngrok processes before starting a new one
    os.system("taskkill /F /IM ngrok.exe /T")

    # ✅ Start a SINGLE Ngrok tunnel for everyone
    public_url = ngrok.connect(port, bind_tls=True).public_url
    print(f"🔥 Ngrok Tunnel is Live: {public_url} (Multiple Users Allowed)")

    # ✅ Run Flask App on 0.0.0.0 to allow external access
    app.run(host="0.0.0.0", port=port, debug=True)
