import os
from app import create_app

# Create Flask app
app = create_app()

if __name__ == '__main__':
    # Use PORT from environment (Render sets this), default to 5000 for local testing
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"

    app.run(host="0.0.0.0", port=port, debug=debug_mode)
