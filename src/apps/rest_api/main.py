import uvicorn

from src.apps.rest_api.frameworks.fastapi.fastapi_server_factory import FastAPIServerFactory
from src.core.configuration.configuration import config

factory = FastAPIServerFactory()
server = factory.create()
app = server.app

if __name__ == "__main__":
    import signal
    import sys

    def handle_exit(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    port = config.get("PORT")
    env = config.get("NODE_ENV")

    reload = env == "development"

    try:
        uvicorn.run(
            "src.apps.rest_api.main:app",
            host="0.0.0.0",
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        pass
