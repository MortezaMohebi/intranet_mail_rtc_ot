# -*- coding: utf-8 -*-
"""Test backend RTC intranet behavior."""

from odoo.addons.mail.tools.discuss import Store
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIntranetRtcBackend(TransactionCase):
    """Validate Discuss RTC backend hardening."""

    def setUp(self):
        """Prepare a Discuss channel and intranet defaults."""
        super().setUp()
        self.params = self.env["ir.config_parameter"].sudo()
        self.params.set_param("intranet_mail_rtc_ot.enabled", "True")
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "False")
        self.params.set_param("intranet_mail_rtc_ot.disable_twilio_rtc", "True")
        self.params.set_param("intranet_mail_rtc_ot.force_empty_ice_servers", "True")
        self.params.set_param("mail.use_twilio_rtc_servers", "False")
        self.channel = self.env["discuss.channel"].create(
            {"name": "RTC Test", "channel_type": "group"}
        )
        self.member = self.channel._find_or_create_member_for_self()

    def test_rtc_join_uses_explicit_empty_ice_servers(self):
        """RTC join returns an explicit empty ICE server list, not False."""
        store = Store()
        self.member.sudo()._rtc_join_call(store=store, camera=False)
        result = store.get_result()
        rtc_records = result.get("Rtc", []) if isinstance(result, dict) else []
        self.assertTrue(rtc_records)
        self.assertEqual(rtc_records[0].get("iceServers"), [])
        self.assertEqual(rtc_records[0].get("iceTransportPolicy"), "all")

    def test_sfu_external_url_rejected(self):
        """External SFU URL is blocked in intranet mode."""
        self.params.set_param("intranet_mail_rtc_ot.allow_local_sfu", "True")
        self.params.set_param("intranet_mail_rtc_ot.allowed_sfu_hosts", "rtc.internal")
        self.params.set_param("mail.sfu_server_url", "https://public.example.com")
        self.assertIsNone(self.member.sudo()._join_sfu(force=True))

    def test_sfu_local_url_policy_allowed(self):
        """Local SFU URL passes policy checks when explicitly allowed."""
        self.params.set_param("intranet_mail_rtc_ot.allow_local_sfu", "True")
        self.params.set_param("intranet_mail_rtc_ot.allowed_sfu_hosts", "rtc.internal")
        self.params.set_param("mail.sfu_server_url", "https://rtc.internal")
        from odoo.addons.intranet_mail_rtc_ot.models.intranet_rtc_policy import is_allowed_sfu_url

        self.assertTrue(is_allowed_sfu_url(self.env, "https://rtc.internal"))

    def test_rtc_join_blocked_when_direct_p2p_disabled_without_local_transport(self):
        """RTC join is blocked when direct P2P fallback is disabled and no local relay exists."""
        self.params.set_param("intranet_mail_rtc_ot.force_empty_ice_servers", "False")
        with self.assertRaises(UserError):
            self.member.sudo()._rtc_join_call(store=Store(), camera=False)
