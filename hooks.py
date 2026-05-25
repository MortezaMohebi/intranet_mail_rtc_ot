# -*- coding: utf-8 -*-
"""Install and uninstall hooks for intranet-safe RTC defaults."""

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

SAFE_DEFAULTS = {
    "intranet_mail_rtc_ot.enabled": "True",
    "intranet_mail_rtc_ot.force_empty_ice_servers": "True",
    "intranet_mail_rtc_ot.allow_custom_local_ice_servers": "False",
    "intranet_mail_rtc_ot.allow_local_sfu": "False",
    "intranet_mail_rtc_ot.allowed_sfu_hosts": "",
    "intranet_mail_rtc_ot.allowed_ice_host_suffixes": ".local,.lan,.internal,.intra",
    "intranet_mail_rtc_ot.disable_twilio_rtc": "True",
    "intranet_mail_rtc_ot.disable_external_push": "True",
    "intranet_mail_rtc_ot.disable_external_gif": "True",
    "intranet_mail_rtc_ot.disable_external_translate": "True",
    "intranet_mail_rtc_ot.disable_external_link_preview": "True",
    "intranet_mail_rtc_ot.use_local_blur_assets": "True",
    "intranet_mail_rtc_ot.debug_rtc_logs": "False",
}

MODULE_PARAMS = tuple(SAFE_DEFAULTS)


def _make_env(env_or_cr, registry=None):
    """Return an Odoo environment for both modern and legacy hook signatures."""
    if hasattr(env_or_cr, "cr") and hasattr(env_or_cr, "uid"):
        return env_or_cr
    return api.Environment(env_or_cr, SUPERUSER_ID, {})


def post_init_hook(env_or_cr, registry=None):
    """Set safe intranet RTC defaults without deleting existing mail data."""
    env = _make_env(env_or_cr, registry=registry)
    params = env["ir.config_parameter"].sudo()
    for key, value in SAFE_DEFAULTS.items():
        if params.get_param(key) in (None, False):
            params.set_param(key, value)
    if params.get_param("intranet_mail_rtc_ot.disable_twilio_rtc", "True") == "True":
        params.set_param("mail.use_twilio_rtc_servers", "False")
    if params.get_param("mail.sfu_server_url"):
        _logger.warning(
            "Intranet RTC installed while mail.sfu_server_url is configured. "
            "Diagnostics will verify whether it is explicitly allowed as local/internal."
        )


def uninstall_hook(env_or_cr, registry=None):
    """Remove only this module's configuration parameters on uninstall."""
    env = _make_env(env_or_cr, registry=registry)
    env["ir.config_parameter"].sudo().search([("key", "in", MODULE_PARAMS)]).unlink()
