import os
import sys

# Add the code/ directory to the import path so tests can import
# lead_qualifier directly (avoids the reserved 'code' package name).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "code"))