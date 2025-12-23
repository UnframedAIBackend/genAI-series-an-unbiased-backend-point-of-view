from fastapi import APIRouter


class HealthRestController:
    def __init__(self) -> None:
        self.router = APIRouter(tags=["health"])
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.router.add_api_route(
            "/health",
            self.health_check,
            methods=["GET"],
            summary="Health check endpoint",
        )

    async def health_check(self) -> dict:
        """Simple health check endpoint for Docker health checks."""
        return {"status": "healthy", "service": "genai-api"}


health_controller = HealthRestController()
router = health_controller.router