from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .route import router as api_router

class FastAPIServerFactory:
    @staticmethod
    def create() -> "FastAPIServer":
        app = FastAPI(
            title="GenAI Series API",
            description="The GenAI Series API documentation",
            version="1.0.0",
            docs_url="/docs",
        )

        # CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Register Routes
        app.include_router(api_router)

        return FastAPIServer(app)

class FastAPIServer:
    def __init__(self, app: FastAPI):
        self.app = app
        self.server = None

    async def listen(self, port: int) -> None:
        config = uvicorn.Config(self.app, host="0.0.0.0", port=port, log_level="info")
        self.server = uvicorn.Server(config)
        await self.server.serve()
