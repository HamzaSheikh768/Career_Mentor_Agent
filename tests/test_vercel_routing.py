import tomllib
import unittest
from pathlib import Path

from api.index import RestoreOriginalPath


class RecordingAsgiApp:
    def __init__(self) -> None:
        self.scope = None

    async def __call__(self, scope, receive, send) -> None:
        self.scope = scope


class VercelRoutingTests(unittest.IsolatedAsyncioTestCase):
    def test_chainlit_uses_websocket_transport(self) -> None:
        config_path = Path(__file__).resolve().parents[1] / ".chainlit" / "config.toml"

        with config_path.open("rb") as config_file:
            chainlit_config = tomllib.load(config_file)

        self.assertEqual(chainlit_config["project"]["transports"], ["websocket"])

    async def test_restores_public_path_and_preserves_socket_query(self) -> None:
        downstream = RecordingAsgiApp()
        middleware = RestoreOriginalPath(downstream)
        scope = {
            "type": "websocket",
            "path": "/api/index",
            "raw_path": b"/api/index",
            "query_string": b"path=ws%2Fsocket.io&EIO=4&transport=websocket",
        }

        async def receive():
            return {}

        async def send(message):
            return None

        await middleware(scope, receive, send)

        self.assertEqual(downstream.scope["path"], "/ws/socket.io")
        self.assertEqual(downstream.scope["raw_path"], b"/ws/socket.io")
        self.assertEqual(
            downstream.scope["query_string"], b"EIO=4&transport=websocket"
        )


if __name__ == "__main__":
    unittest.main()
