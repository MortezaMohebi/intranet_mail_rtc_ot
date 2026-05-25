# -*- coding: utf-8 -*-
"""Test intranet ICE server validation."""

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIceValidation(TransactionCase):
    """Validate local-only ICE policy behavior."""

    def setUp(self):
        """Prepare configuration for validation tests."""
        super().setUp()
        self.params = self.env["ir.config_parameter"].sudo()
        self.params.set_param("intranet_mail_rtc_ot.enabled", "True")
        self.params.set_param("intranet_mail_rtc_ot.disable_twilio_rtc", "True")
        self.params.set_param("intranet_mail_rtc_ot.allowed_ice_host_suffixes", ".local,.lan,.internal,.intra")
        self.env["mail.ice.server"].sudo().search([]).unlink()

    def test_custom_ice_ignored_when_not_allowed(self):
        """Configured ICE is ignored while custom local ICE is disabled."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "False")
        self.env["mail.ice.server"].sudo().create({"server_type": "turn", "uri": "10.0.0.5:3478"})
        self.assertEqual(self.env["mail.ice.server"]._get_ice_servers(), [])

    def test_private_ice_allowed_when_configured(self):
        """Private ICE hosts are allowed when custom local ICE is enabled."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        self.env["mail.ice.server"].sudo().create({"server_type": "turn", "uri": "10.0.0.5:3478"})
        servers = self.env["mail.ice.server"]._get_ice_servers()
        self.assertEqual(servers[0]["urls"], "turn:10.0.0.5:3478")

    def test_internal_domain_allowed_when_configured(self):
        """Internal suffix ICE hosts are accepted."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        self.env["mail.ice.server"].sudo().create({"server_type": "stun", "uri": "rtc.lan:3478"})
        self.assertEqual(self.env["mail.ice.server"]._get_ice_servers()[0]["urls"], "stun:rtc.lan:3478")

    def test_public_ice_rejected(self):
        """Public ICE hosts are rejected in intranet mode."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        self.env["mail.ice.server"].sudo().create({"server_type": "stun", "uri": "public.example.com:19302"})
        self.assertEqual(self.env["mail.ice.server"]._get_ice_servers(), [])

    def test_credentials_not_in_result_when_server_rejected(self):
        """Rejected TURN credentials are not returned to the frontend."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        self.env["mail.ice.server"].sudo().create(
            {
                "server_type": "turn",
                "uri": "public.example.com:3478",
                "username": "secret-user",
                "credential": "secret-password",
            }
        )
        self.assertEqual(self.env["mail.ice.server"]._get_ice_servers(), [])
