# -*- coding: utf-8 -*-
"""Restrict ICE server resolution to local intranet-safe servers."""

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .intranet_rtc_policy import (
    build_ice_url,
    debug_log,
    get_bool_param,
    is_enabled,
    is_valid_ice_port,
    normalize_ice_uri,
    sanitize_ice_servers,
    split_ice_uri,
)

_logger = logging.getLogger(__name__)


class MailIceServer(models.Model):
    """Apply intranet policy to Odoo's ICE server provider."""

    _inherit = "mail.ice.server"

    server_type = fields.Selection(
        selection_add=[("turns", "turns:")],
        ondelete={"turns": "cascade"},
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Normalize ICE URI values before records are inserted."""
        for vals in vals_list:
            if vals.get("uri"):
                vals["uri"] = normalize_ice_uri(vals["uri"])
        return super().create(vals_list)

    def write(self, vals):
        """Normalize ICE URI values before records are updated."""
        if vals.get("uri"):
            vals = dict(vals, uri=normalize_ice_uri(vals["uri"]))
        return super().write(vals)

    @api.constrains("server_type", "uri", "username", "credential")
    def _check_intranet_rtc_ice_server(self):
        """Validate TURN/STUN/TURNS records before they are used by browsers."""
        for server in self:
            uri = normalize_ice_uri(server.uri)
            host, port, _query = split_ice_uri(uri)
            if not host:
                raise ValidationError("ICE server URI must include a host name or IP address.")
            if not is_valid_ice_port(port):
                raise ValidationError(
                    "ICE server port must use English digits and be a valid "
                    "TCP/UDP port number between 1 and 65535."
                )
            if server.server_type in {"turn", "turns"} and (
                not server.username or not server.credential
            ):
                raise ValidationError(
                    "TURN and TURNS ICE servers require both username and credential."
                )

    def _get_local_ice_servers(self):
        """Return local ICE servers formatted for browser RTCConfiguration.

        Odoo core stores the scheme in ``server_type`` and the rest of the URL
        in ``uri``. This override adds ``turns`` support and always normalizes
        the URI part before final URL generation, preventing double-prefix
        browser URLs.
        """
        formatted_ice_servers = []
        for ice_server in self.sudo().search([], limit=5):
            try:
                ice_url = build_ice_url(ice_server.server_type, ice_server.uri)
            except Exception:  # noqa: BLE001 - keep invalid admin data from breaking calls.
                _logger.warning(
                    "Skipping invalid ICE server configuration id=%s type=%s.",
                    ice_server.id,
                    ice_server.server_type,
                )
                continue
            formatted_ice_server = {"urls": ice_url}
            if ice_server.server_type in {"turn", "turns"}:
                if not ice_server.username or not ice_server.credential:
                    _logger.warning(
                        "Skipping %s ICE server id=%s because username or credential is missing.",
                        ice_server.server_type,
                        ice_server.id,
                    )
                    continue
                formatted_ice_server["username"] = ice_server.username
                formatted_ice_server["credential"] = ice_server.credential
            elif ice_server.username:
                formatted_ice_server["username"] = ice_server.username
            if ice_server.server_type == "stun" and ice_server.credential:
                formatted_ice_server["credential"] = ice_server.credential
            formatted_ice_servers.append(formatted_ice_server)
        return formatted_ice_servers

    def _get_ice_servers(self):
        """Return only intranet-safe ICE servers when intranet RTC mode is enabled."""
        if not is_enabled(self.env):
            servers = super()._get_ice_servers()
            debug_log(
                self.env,
                "ICE provider: intranet mode disabled; returning Odoo default count=%s.",
                len(servers or []),
            )
            return servers
        if get_bool_param(self.env, "intranet_mail_rtc_ot.disable_twilio_rtc", default=True):
            local_servers = self._get_local_ice_servers()
            debug_log(
                self.env,
                "ICE provider: Twilio disabled; local mail.ice.server count before sanitize=%s.",
                len(local_servers or []),
            )
        else:
            local_servers = super()._get_ice_servers()
            debug_log(
                self.env,
                "ICE provider: Twilio not disabled; Odoo ICE count before sanitize=%s.",
                len(local_servers or []),
            )
        sanitized = sanitize_ice_servers(self.env, local_servers)
        debug_log(
            self.env,
            "ICE provider: effective ICE count sent to client=%s.",
            len(sanitized or []),
        )
        return sanitized
