# main.py - This is the ENTRY POINT for Pxxl
import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Get WSGI application
application = get_wsgi_application()

# Optional: For running locally
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)