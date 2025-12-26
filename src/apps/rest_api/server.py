from .frameworks.fastapi.fastapi_server_factory import FastAPIServerFactory


class Server:
    servers = {
        "fastapi": FastAPIServerFactory,
    }

    def __init__(self) -> None:
        self.server = None

    async def run(self, port: int) -> None:
        framework = "fastapi"
        self.server = self.servers[framework].create()
        await self.server.listen(port)
