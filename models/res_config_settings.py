# -*- coding: utf-8 -*-
"""Settings fields for intranet RTC hardening."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose intranet RTC policy options in Discuss settings."""

    _inherit = "res.config.settings"

    intranet_rtc_enabled = fields.Boolean(
        string="Enable Intranet RTC Mode",
        config_parameter="intranet_mail_rtc_ot.enabled",
        default=True,
        help="Prevent Discuss calls from using public STUN/TURN/SFU services.",
    )
    intranet_rtc_force_empty_ice_servers = fields.Boolean(
        string="Force Empty ICE Servers",
        config_parameter="intranet_mail_rtc_ot.force_empty_ice_servers",
        default=True,
        help="Send an explicit empty iceServers list when no local ICE server is allowed.",
    )
    intranet_rtc_allow_custom_local_ice_servers = fields.Boolean(
        string="Allow Custom Local ICE Servers",
        config_parameter="intranet_mail_rtc_ot.allow_custom_local_ice_servers",
        default=False,
        help="Allow only private/local STUN or TURN records configured in Discuss ICE Servers.",
    )
    intranet_rtc_allowed_ice_host_suffixes = fields.Char(
        string="Allowed Internal ICE Host Suffixes",
        config_parameter="intranet_mail_rtc_ot.allowed_ice_host_suffixes",
        default=".local,.lan,.internal,.intra",
        help="Comma-separated suffixes that are considered internal for ICE hosts.",
    )
    intranet_rtc_allow_local_sfu = fields.Boolean(
        string="Allow Local SFU",
        config_parameter="intranet_mail_rtc_ot.allow_local_sfu",
        default=False,
        help="Allow Odoo Discuss to use an SFU only when its host is explicitly local/internal.",
    )
    intranet_rtc_allowed_sfu_hosts = fields.Char(
        string="Allowed SFU Hosts",
        config_parameter="intranet_mail_rtc_ot.allowed_sfu_hosts",
        help="Comma-separated local/internal SFU hosts or suffixes allowed in intranet mode.",
    )
    intranet_rtc_disable_twilio_rtc = fields.Boolean(
        string="Disable Twilio RTC",
        config_parameter="intranet_mail_rtc_ot.disable_twilio_rtc",
        default=True,
        help="Prevent Odoo from requesting Twilio RTC tokens while intranet RTC mode is enabled.",
    )
    intranet_rtc_disable_external_push = fields.Boolean(
        string="Disable External Web Push",
        config_parameter="intranet_mail_rtc_ot.disable_external_push",
        default=True,
        help="Disable browser push endpoint calls that leave the Odoo intranet.",
    )
    intranet_rtc_disable_external_gif = fields.Boolean(
        string="Disable Tenor GIF",
        config_parameter="intranet_mail_rtc_ot.disable_external_gif",
        default=True,
        help="Disable Tenor GIF API calls from Discuss.",
    )
    intranet_rtc_disable_external_translate = fields.Boolean(
        string="Disable Google Translate",
        config_parameter="intranet_mail_rtc_ot.disable_external_translate",
        default=True,
        help="Disable Google Translate API calls from Discuss messages.",
    )
    intranet_rtc_disable_external_link_preview = fields.Boolean(
        string="Disable External Link Preview",
        config_parameter="intranet_mail_rtc_ot.disable_external_link_preview",
        default=True,
        help="Disable server-side fetching of external URLs for link previews.",
    )
    intranet_rtc_use_local_blur_assets = fields.Boolean(
        string="Use Local Background Blur Assets",
        config_parameter="intranet_mail_rtc_ot.use_local_blur_assets",
        default=True,
        help="Serve MediaPipe Selfie Segmentation files from this Odoo module instead of a CDN.",
    )
    intranet_rtc_debug_logs = fields.Boolean(
        string="Debug RTC Logs",
        config_parameter="intranet_mail_rtc_ot.debug_rtc_logs",
        default=False,
        help="Enable limited debug logs without exposing secrets.",
    )

    def action_open_intranet_rtc_diagnostics(self):
        """Open a fresh intranet RTC diagnostics wizard."""
        wizard = self.env["intranet.rtc.diagnostic"].create({})
        wizard.action_run_diagnostics()
        return {
            "type": "ir.actions.act_window",
            "name": "Intranet RTC Diagnostics",
            "res_model": "intranet.rtc.diagnostic",
            "view_mode": "form",
            "res_id": wizard.id,
            "target": "new",
            "view_id": self.env.ref("intranet_mail_rtc_ot.intranet_rtc_diagnostic_view_form").id,
        }
