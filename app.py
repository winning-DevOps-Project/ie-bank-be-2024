import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware

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

# Set up Flask-Migrate
migrate = Migrate(app, db)

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    logger.info(f"Starting Flask app in debug mode: {debug_mode}")
    app.run(debug=debug_mode)
