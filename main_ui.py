# main_ui.py
import os
import webbrowser
from http.server import HTTPServer

import scrape.config as config
from web.server import Handler


def main() -> None:
    """Start the HTTP server and open browser."""
    db_path = os.path.abspath(config.DB_FILE)
    print(f"DB FILE: {db_path}")

    port = 8080
    url = f"http://localhost:{port}"
    print(url)
    webbrowser.open(url)

    server = HTTPServer(("", port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    main()
