import os
import webbrowser
from wsgiref.simple_server import make_server

import scrape.config as config
from web.app import app


def main() -> None:
    db_path = os.path.abspath(config.DB_FILE)
    print(f"DB FILE: {db_path}")

    port = 8080
    url = f"http://localhost:{port}"
    print(url)
    webbrowser.open(url)

    server = make_server("", port, app)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    main()
