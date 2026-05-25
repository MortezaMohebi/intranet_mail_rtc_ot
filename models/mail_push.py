# -*- coding: utf-8 -*-
"""Disable external web push delivery in intranet mode."""

from odoo import api, models

from .intranet_rtc_policy import get_bool_param, is_enabled


class MailPush(models.Model):
    """Prevent queued browser push notifications from leaving the intranet."""

    _inherit = "mail.push"

    @api.model
    def _push_notification_to_endpoint(self, batch_size=50):
        """Drop queued push notifications when external push is disabled."""
        if is_enabled(self.env) and get_bool_param(
            self.env,
            "intranet_mail_rtc_ot.disable_external_push",
            default=True,
        ):
            self.sudo().search([], limit=batch_size).unlink()
            return None
        return super()._push_notification_to_endpoint(batch_size=batch_size)
