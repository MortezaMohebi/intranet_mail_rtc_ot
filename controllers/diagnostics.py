# -*- coding: utf-8 -*-
"""Controllers for diagnostics and external Discuss feature blocking."""

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.http import request, route
from odoo.addons.mail.controllers.discuss.gif import DiscussGifController
from odoo.addons.mail.controllers.google_translate import GoogleTranslateController

from ..models.intranet_rtc_policy import get_bool_param, is_enabled


class IntranetRtcDiagnosticController(http.Controller):
    """Expose safe diagnostics to administrators only."""

    @http.route("/intranet_mail_rtc_ot/diagnostics", type="json", auth="user")
    def diagnostics(self):
        """Return current intranet RTC diagnostics without secrets."""
        if not request.env.user.has_group("base.group_system"):
            raise Forbidden()
        wizard = request.env["intranet.rtc.diagnostic"].sudo().create({})
        diagnostics, warnings = wizard._build_diagnostics()
        diagnostics["warnings"] = warnings.split("\n") if warnings else []
        return diagnostics


class IntranetDiscussGifController(DiscussGifController):
    """Disable Tenor GIF calls when configured for intranet mode."""

    def _is_disabled(self):
        """Return whether external GIF calls are disabled."""
        return is_enabled(request.env) and get_bool_param(
            request.env,
            "intranet_mail_rtc_ot.disable_external_gif",
            default=True,
        )

    @route("/discuss/gif/search", type="json", auth="user")
    def search(self, search_term, locale="en", country="US", position=None, readonly=True):
        """Return an empty GIF result instead of calling Tenor."""
        if self._is_disabled():
            return {"results": [], "next": ""}
        return super().search(search_term, locale=locale, country=country, position=position, readonly=readonly)

    @route("/discuss/gif/categories", type="json", auth="user", readonly=True)
    def categories(self, locale="en", country="US"):
        """Return no GIF categories instead of calling Tenor."""
        if self._is_disabled():
            return {"tags": []}
        return super().categories(locale=locale, country=country)

    @route("/discuss/gif/favorites", type="json", auth="user", readonly=True)
    def get_favorites(self, offset=0):
        """Return no remote GIF favorites while external GIFs are disabled."""
        if self._is_disabled():
            return ([],)
        return super().get_favorites(offset=offset)


class IntranetGoogleTranslateController(GoogleTranslateController):
    """Disable Google Translate calls when configured for intranet mode."""

    @route("/mail/message/translate", type="json", auth="user")
    def translate(self, message_id):
        """Return a clean disabled response instead of calling Google Translate."""
        if is_enabled(request.env) and get_bool_param(
            request.env,
            "intranet_mail_rtc_ot.disable_external_translate",
            default=True,
        ):
            return {"error": "Message translation is disabled in intranet RTC mode."}
        return super().translate(message_id)
