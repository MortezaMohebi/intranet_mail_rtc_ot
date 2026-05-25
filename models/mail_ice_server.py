# -*- coding: utf-8 -*-
"""Restrict ICE server resolution to local intranet-safe servers."""

import logging

from odoo import models

from .intranet_rtc_policy import (
    debug_log,
    get_bool_param,
    is_enabled,
    sanitize_ice_servers,
)

_logger = logging.getLogger(__name__)


class MailIceServer(models.Model):
    """Apply intranet policy to Odoo's ICE server provider."""

    _inherit = "mail.ice.server"

    def _get_ice_servers(self):
        """Return only intranet-safe ICE servers when intranet RTC mode is enabled."""
        if not is_enabled(self.env):
            servers = super()._get_ice_servers()
            debug_log(self.env, "ICE provider: intranet mode disabled; returning Odoo default count=%s.", len(servers or []))
            return servers
        if get_bool_param(self.env, "intranet_mail_rtc_ot.disable_twilio_rtc", default=True):
            local_servers = super()._get_local_ice_servers()
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
        debug_log(self.env, "ICE provider: effective ICE count sent to client=%s.", len(sanitized or []))
        return sanitized
