import asyncio
import base64
import hashlib
import os

from aiohttp import web


def generate_pkce_pair() -> tuple[str, str]:
    """Generate a PKCE code verifier and code challenge pair.

    Returns
    -------
    tuple[str, str]
        A tuple of (code_verifier, code_challenge).
    """
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("ascii")
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


def generate_state() -> str:
    """Generate a random state string for OAuth CSRF protection."""
    return base64.urlsafe_b64encode(os.urandom(24)).rstrip(b"=").decode("ascii")


_CALLBACK_HTML = """<!DOCTYPE html>
<html>
<body>
<p>Authorization complete. You can close this page.</p>
</body>
</html>"""


class OAuthCallbackServer:
    """A minimal local HTTP server to capture the OAuth redirect callback."""

    def __init__(self) -> None:
        self._future: asyncio.Future[str] | None = None
        self._app = web.Application()
        self._app.router.add_get("/callback", self._handle_callback)
        self._runner: web.AppRunner | None = None

    async def _handle_callback(self, request: web.Request) -> web.Response:
        code = request.query.get("code")
        state = request.query.get("state")
        error = request.query.get("error")

        if error:
            if self._future and not self._future.done():
                self._future.set_exception(RuntimeError(f"OAuth error: {error}"))
            return web.Response(text=f"Authorization failed: {error}", content_type="text/html")

        if not code:
            if self._future and not self._future.done():
                self._future.set_exception(RuntimeError("No authorization code received."))
            return web.Response(text="No code received.", content_type="text/html")

        if self._future and not self._future.done():
            self._future.set_result((code, state))

        return web.Response(text=_CALLBACK_HTML, content_type="text/html")

    async def start(self, port: int, timeout: float = 300) -> tuple[str, str]:
        """Start the callback server and wait for the OAuth callback.

        Parameters
        ----------
        port: int
            The port to listen on.
        timeout: float
            Maximum seconds to wait for the callback. Defaults to 300 (5 minutes).

        Returns
        -------
        tuple[str, str]
            A tuple of (authorization_code, state) when the callback is received.

        Raises
        ------
        TimeoutError
            If the callback is not received within the timeout.
        """
        loop = asyncio.get_running_loop()
        self._future = loop.create_future()
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, "localhost", port)
        await site.start()
        return await asyncio.wait_for(self._future, timeout=timeout)

    async def stop(self) -> None:
        """Stop the callback server."""
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
