# -*- coding: utf-8 -*-
"""Make Discuss RTC join responses explicit and intranet-safe."""

import logging

from odoo import _, models
from odoo.exceptions import UserError
from odoo.addons.mail.tools.discuss import Store

from .intranet_rtc_policy import (
    debug_log,
    is_allowed_sfu_url,
    is_direct_p2p_fallback_enabled,
    is_enabled,
    get_ice_transport_policy,
    sanitize_ice_servers,
)

_logger = logging.getLogger(__name__)


class DiscussChannelMember(models.Model):
    """Patch RTC join and SFU upgrade behavior for locked intranets."""

    _inherit = "discuss.channel.member"


    def _intranet_rtc_has_allowed_transport(self):
        """Return whether RTC has an allowed P2P, ICE, or SFU transport."""
        if not is_enabled(self.env):
            return True
        if is_direct_p2p_fallback_enabled(self.env):
            return True
        effective_ice_servers = self.env["mail.ice.server"]._get_ice_servers() or []
        if effective_ice_servers:
            return True
        sfu_url = self.env["ir.config_parameter"].sudo().get_param("mail.sfu_server_url")
        return bool(sfu_url and is_allowed_sfu_url(self.env, sfu_url))

    def _rtc_join_call(self, store=None, check_rtc_session_ids=None, camera=False):
        """Join an RTC call and force explicit empty ICE servers when required."""
        debug_log(
            self.env,
            "RTC join: channel_ids=%s member_ids=%s camera=%s store=%s intranet_enabled=%s direct_p2p_fallback=%s.",
            self.mapped("channel_id").ids,
            self.ids,
            camera,
            bool(store),
            is_enabled(self.env),
            is_direct_p2p_fallback_enabled(self.env),
        )
        if is_enabled(self.env) and not self._intranet_rtc_has_allowed_transport():
            raise UserError(
                _(
                    "Intranet RTC direct P2P fallback is disabled, but no validated "
                    "local ICE server or allowed local SFU is configured. Configure a "
                    "local TURN/STUN/SFU server, or enable Direct P2P Fallback in "
                    "Discuss settings."
                )
            )
        result = super()._rtc_join_call(
            store=store,
            check_rtc_session_ids=check_rtc_session_ids,
            camera=camera,
        )
        if is_enabled(self.env) and store:
            effective_ice_servers = self.env["mail.ice.server"]._get_ice_servers() or []
            server_info = self._get_rtc_server_info(
                self.rtc_session_ids[:1],
                effective_ice_servers,
            )
            debug_log(
                self.env,
                "RTC join: forcing explicit iceServers list count=%s server_info=%s.",
                len(effective_ice_servers),
                bool(server_info),
            )
            store.add(
                "Rtc",
                {
                    "iceServers": effective_ice_servers,
                    "iceTransportPolicy": get_ice_transport_policy(self.env),
                    "serverInfo": server_info,
                },
            )
        return result

    def _join_sfu(self, ice_servers=None, force=False):
        """Join SFU only when it is explicitly configured as local/internal."""
        if not is_enabled(self.env):
            return super()._join_sfu(ice_servers=ice_servers, force=force)
        sfu_url = self.env["ir.config_parameter"].sudo().get_param("mail.sfu_server_url")
        if not sfu_url or not is_allowed_sfu_url(self.env, sfu_url):
            if self.channel_id.sfu_channel_uuid or self.channel_id.sfu_server_url:
                self.channel_id.sfu_channel_uuid = None
                self.channel_id.sfu_server_url = None
            if sfu_url:
                _logger.warning("Blocked non-local or disallowed SFU URL in intranet RTC mode.")
            debug_log(self.env, "RTC SFU: skipped; configured=%s allowed=False.", bool(sfu_url))
            return None
        debug_log(self.env, "RTC SFU: allowed local/internal SFU URL.")
        return super()._join_sfu(
            ice_servers=sanitize_ice_servers(self.env, ice_servers or []),
            force=force,
        )

    def _get_rtc_server_info(self, rtc_session, ice_servers=None, key=None):
        """Return SFU server info only if the SFU URL passes intranet policy."""
        if is_enabled(self.env):
            sfu_url = self.channel_id.sfu_server_url or self.env["ir.config_parameter"].sudo().get_param(
                "mail.sfu_server_url"
            )
            if not sfu_url or not is_allowed_sfu_url(self.env, sfu_url):
                debug_log(self.env, "RTC serverInfo: no allowed SFU info returned.")
                return None
            ice_servers = sanitize_ice_servers(self.env, ice_servers or [])
            debug_log(self.env, "RTC serverInfo: allowed local SFU with ICE count=%s.", len(ice_servers))
        return super()._get_rtc_server_info(rtc_session, ice_servers=ice_servers, key=key)
