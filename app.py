import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware

from dotenv import load_dotenv

load_dotenv()

app = Flask(_name_)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)

@app.route("/")
def index():
    return "Database configured successfully!"

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

from flask_migrate import Migrate

from iebank_api import create_app, db

# Create the app instance using the factory pattern
app = create_app()

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

# Run database migrations
migrate = Migrate(app, db)

# Initialize the database
with app.app_context():
    db.create_all()
    logger.info("Database tables created or already exist.")

# Define a sample route for testing
@app.route('/')
def home():
    logger.info("Home route accessed")
    return "Welcome to IE Bank Backend!"

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    logger.info(f"Starting Flask app in debug mode: {debug_mode}")
    app.run(debug=debug_mode)
