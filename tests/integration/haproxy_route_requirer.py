# pylint: disable=import-error
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""haproxy-route requirer source."""

import typing
from collections.abc import Buffer
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import ops
from any_charm_base import AnyCharmBase  # type: ignore
from haproxy_route import HaproxyRouteRequirer, RateLimitPolicy  # type: ignore

HAPROXY_ROUTE_RELATION = "require-haproxy-route"
PORT = 8080


class Handler(BaseHTTPRequestHandler):
    """HTTP requests handler class."""

    # pylint: disable=invalid-name
    def do_GET(self):  # noqa
        """Handle incoming GET requests."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(typing.cast(Buffer, f"GET request for {self.path}"))


# pylint: disable=too-few-public-methods
class AnyCharm(AnyCharmBase):
    """haproxy-route requirer charm."""

    def __init__(self, *args, **kwargs):
        """Initialize the requirer charm."""  # noqa
        super().__init__(*args, **kwargs)
        self._haproxy_route = HaproxyRouteRequirer(self, HAPROXY_ROUTE_RELATION)
        self.server = Thread(target=start_server)
        self.server.run()
        self.unit.status = ops.ActiveStatus(f"Server listening on port {PORT}")

    def update_relation(self):
        """Update relation details for haproxy-route."""
        self._haproxy_route.provide_haproxy_route_requirements(
            service="any",
            ports=[80],
            subdomains=["ok", "ok2"],
            rate_limit_connections_per_minute=1,
            rate_limit_policy=RateLimitPolicy.DENY,
            check_interval=600,
            check_rise=3,
            check_fall=3,
            check_path="/ok",
            path_rewrite_expressions=["/ok"],
            deny_paths=["/private"],
        )


def start_server() -> None:
    """Start the HTTP server."""
    httpd = HTTPServer(("", PORT), Handler)
    httpd.serve_forever()
