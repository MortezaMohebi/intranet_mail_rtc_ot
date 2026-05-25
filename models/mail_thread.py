# -*- coding: utf-8 -*-
"""Disable direct web push notification dispatch in intranet mode."""

from odoo import models

from .intranet_rtc_policy import get_bool_param, is_enabled


class MailThread(models.AbstractModel):
    """Prevent immediate browser push endpoint calls when disabled."""

    _inherit = "mail.thread"

    def _notify_thread_by_web_push(self, message, recipients_data, msg_vals=False, **kwargs):
        """Skip web push delivery while preserving normal inbox/bus messaging."""
        if is_enabled(self.env) and get_bool_param(
            self.env,
            "intranet_mail_rtc_ot.disable_external_push",
            default=True,
        ):
            return None
        return super()._notify_thread_by_web_push(
            message,
            recipients_data,
            msg_vals=msg_vals,
            **kwargs,
        )
