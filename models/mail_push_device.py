# -*- coding: utf-8 -*-
"""Prevent browser push device registration in intranet mode."""

from odoo import api, models

from .intranet_rtc_policy import get_bool_param, is_enabled


class MailPushDevice(models.Model):
    """Avoid creating public web push subscriptions when disabled."""

    _inherit = "mail.push.device"

    @api.model
    def get_web_push_vapid_public_key(self):
        """Return no VAPID key when external web push is disabled."""
        if is_enabled(self.env) and get_bool_param(
            self.env,
            "intranet_mail_rtc_ot.disable_external_push",
            default=True,
        ):
            return False
        return super().get_web_push_vapid_public_key()

    @api.model
    def register_devices(self, **kw):
        """Ignore browser push subscription attempts when disabled."""
        if is_enabled(self.env) and get_bool_param(
            self.env,
            "intranet_mail_rtc_ot.disable_external_push",
            default=True,
        ):
            return None
        return super().register_devices(**kw)
