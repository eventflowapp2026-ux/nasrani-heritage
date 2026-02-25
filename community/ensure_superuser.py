# community/ensure_superuser.py
import os
import sys
import django

# Add the project root directory to the Python path
# This ensures 'nasrani_heritage.settings' can be found
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added {project_root} to Python path")

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nasrani_heritage.settings')

# Configure Django
try:
    django.setup()
    print("Django setup successful.")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.contrib.auth import get_user_model

def create_superuser():
    """Create a superuser from environment variables if it doesn't exist"""
    # Get credentials from environment variables
    username = os.environ.get('ADMIN_USERNAME')
    email = os.environ.get('ADMIN_EMAIL')
    password = os.environ.get('ADMIN_PASSWORD')
    
    # Check if all required variables are set
    if not (username and email and password):
        print("⚠️  Admin credentials not set in environment variables.")
        print("Set ADMIN_USERNAME, ADMIN_EMAIL, and ADMIN_PASSWORD in Render dashboard.")
        return False
    
    # Get the User model
    User = get_user_model()
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"✓ Superuser '{username}' already exists")
        return True
    
    # Create the superuser
    try:
        User.objects.create_superuser(username, email, password)
        print(f"✅ Superuser '{username}' created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
        return False

if __name__ == "__main__":
    success = create_superuser()
    if not success:
        # Exit with error code to potentially halt build if needed? 
        # For now, just report. Build will continue.
        pass
