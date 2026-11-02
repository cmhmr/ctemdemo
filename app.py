"""Entry point: `python app.py` starts the CTEM Demo Store on CTEM_HOST:CTEM_PORT."""

import os

from ctem_demo import create_app

app = create_app()

if __name__ == "__main__":
    # Defaults to loopback for local runs; the container sets CTEM_HOST=0.0.0.0.
    host = os.environ.get("CTEM_HOST", "127.0.0.1")
    port = int(os.environ.get("CTEM_PORT", "8080"))
    app.run(host=host, port=port, debug=False)
