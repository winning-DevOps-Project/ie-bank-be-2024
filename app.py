from flask import Flask
import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware

from iebank_api import db
from iebank_api.routes import api  # Import the blueprint
from iebank_api.models import User, Account  # Ensure User and Account models are loaded

# Initialize Flask app
app = Flask("hello")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Update as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Register the blueprint
app.register_blueprint(api)

# Set up Application Insights instrumentation key
instrumentation_key = os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY", "00000000-0000-0000-0000-000000000000")

# Initialize Application Insights Middleware for tracing
middleware = FlaskMiddleware(
    app,
    exporter=AzureExporter(connection_string=f'InstrumentationKey={instrumentation_key}'),
    sampler=ProbabilitySampler(rate=1.0),
)

# Set up Azure LogHandler for logging
logger = logging.getLogger("Hello")
logger.setLevel(logging.INFO)
logger.addHandler(AzureLogHandler(connection_string=f'InstrumentationKey={instrumentation_key}'))

# Log application initialization
with app.app_context():
    db.create_all()  # Creates tables for the User and Account models if not existing
    logger.info("Database tables created or already exist.")

# Define a sample route with logging
@app.route('/')
def home():
    logger.info("Home route accessed")
    return "Welcome to IE Bank Backend!"

if __name__ == 'main':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    logger.info(f"Starting Flask app in debug mode: {debug_mode}")
    app.run(debug=debug_mode)