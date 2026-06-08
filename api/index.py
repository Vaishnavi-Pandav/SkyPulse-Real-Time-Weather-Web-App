import sys
import os

# Add the project root (one level up from api/) to the Python path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

# Set working directory to project root so Flask finds templates/ and static/
os.chdir(root)

from app import app

handler = app
