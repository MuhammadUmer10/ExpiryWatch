from flask import Flask
from database import init_db
from scheduler import start_scheduler
from routes.services import service_bp
from routes.licenses import license_bp
from routes.auth_routes import auth_bp
from config import (
    SERVER_PORT
)
app = Flask(__name__)
init_db()


app.register_blueprint(service_bp, url_prefix='/services')
app.register_blueprint(license_bp, url_prefix='/licenses')
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == "__main__":
    start_scheduler()
    port=SERVER_PORT
    app.run(debug=True, port=port)
