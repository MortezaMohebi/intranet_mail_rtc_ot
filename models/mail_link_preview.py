# -*- coding: utf-8 -*-
"""Disable external link preview fetching in intranet mode."""

from odoo import api, models

from .intranet_rtc_policy import get_bool_param, is_enabled


class MailLinkPreview(models.Model):
    """Prevent server-side external URL fetching for link previews."""

    _inherit = "mail.link.preview"

    @api.model
    def _is_link_preview_enabled(self):
        """Return False when intranet mode disables external link previews."""
        if is_enabled(self.env) and get_bool_param(
            self.env,
            "intranet_mail_rtc_ot.disable_external_link_preview",
            default=True,
        ):
            return False
        return super()._is_link_preview_enabled()

    @api.model
    def _create_from_message_and_notify(self, message, request_url=None):
        """Skip link preview fetches when disabled by intranet policy."""
        if not self._is_link_preview_enabled():
            return self
        return super()._create_from_message_and_notify(message, request_url=request_url)
