#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Learn more at: https://juju.is/docs/sdk

"""haproxy-operator charm file."""

import logging
import typing

import ops

import haproxy

logger = logging.getLogger(__name__)


class HAProxyCharm(ops.CharmBase):
    """Charm haproxy."""

    def __init__(self, *args: typing.Any):
        """Initialize the charm and register event handlers.

        Args:
            args: Arguments to initialize the charm base.
        """
        super().__init__(*args)
        self.haproxy_service = haproxy.HAProxyService()
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

    def _on_install(self, _: typing.Any) -> None:
        """Install the haproxy package.

        Raises:
            RuntimeError: When the haproxy service is not running after install.
        """
        self.haproxy_service.install()
        if not self.haproxy_service.is_active:
            logger.error("HAProxy service is not running.")
            raise RuntimeError("Service not running.")
        self.unit.status = ops.ActiveStatus()

    def _on_config_changed(self, _: typing.Any) -> None:
        """Handle the config-changed event."""
        self.haproxy_service.render_haproxy_config()


if __name__ == "__main__":  # pragma: nocover
    ops.main.main(HAProxyCharm)
