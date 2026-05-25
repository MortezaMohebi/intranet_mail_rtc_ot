# -*- coding: utf-8 -*-
"""Test intranet ICE server validation."""

from odoo.exceptions import ValidationError
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
        self.params.set_param(
            "intranet_mail_rtc_ot.allowed_ice_host_suffixes",
            ".local,.lan,.internal,.intra",
        )
        self.env["mail.ice.server"].sudo().search([]).unlink()

    def test_custom_ice_ignored_when_not_allowed(self):
        """Configured ICE is ignored while custom local ICE is disabled."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "False")
        self.env["mail.ice.server"].sudo().create(
            {
                "server_type": "turn",
                "uri": "10.0.0.5:3478",
                "username": "u",
                "credential": "p",
            }
        )
        self.assertEqual(self.env["mail.ice.server"]._get_ice_servers(), [])

    def test_private_ice_allowed_when_configured(self):
        """Private ICE hosts are allowed when custom local ICE is enabled."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        self.env["mail.ice.server"].sudo().create(
            {
                "server_type": "turn",
                "uri": "10.0.0.5:3478",
                "username": "u",
                "credential": "p",
            }
        )
        servers = self.env["mail.ice.server"]._get_ice_servers()
        self.assertEqual(servers[0]["urls"], "turn:10.0.0.5:3478")
        self.assertEqual(servers[0]["username"], "u")
        self.assertEqual(servers[0]["credential"], "p")

    def test_turns_ice_allowed_and_generates_correct_url(self):
        """TURNS records are accepted and generated without double prefixes."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        self.env["mail.ice.server"].sudo().create(
            {
                "server_type": "turns",
                "uri": "turns:10.0.0.5:443?transport=tcp",
                "username": "u",
                "credential": "p",
            }
        )
        servers = self.env["mail.ice.server"]._get_ice_servers()
        self.assertEqual(servers[0]["urls"], "turns:10.0.0.5:443?transport=tcp")
        self.assertEqual(servers[0]["username"], "u")
        self.assertEqual(servers[0]["credential"], "p")

    def test_turns_public_host_allowed_when_suffix_configured(self):
        """Explicitly configured internal suffixes may allow non-private TURNS hosts."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        self.params.set_param("intranet_mail_rtc_ot.allowed_ice_host_suffixes", "turn.example.com")
        self.env["mail.ice.server"].sudo().create(
            {
                "server_type": "turns",
                "uri": "turn.example.com:443?transport=tcp",
                "username": "u",
                "credential": "p",
            }
        )
        servers = self.env["mail.ice.server"]._get_ice_servers()
        self.assertEqual(servers[0]["urls"], "turns:turn.example.com:443?transport=tcp")

    def test_persian_port_digits_are_normalized(self):
        """Persian and Arabic port digits are normalized before ICE URL generation."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        record = self.env["mail.ice.server"].sudo().create(
            {
                "server_type": "turns",
                "uri": "10.0.0.5:۴۴۳?transport=tcp",
                "username": "u",
                "credential": "p",
            }
        )
        self.assertEqual(record.uri, "10.0.0.5:443?transport=tcp")
        self.assertEqual(
            self.env["mail.ice.server"]._get_ice_servers()[0]["urls"],
            "turns:10.0.0.5:443?transport=tcp",
        )


    def test_invalid_ice_port_is_rejected(self):
        """Invalid ports are rejected before they reach browser ICE config."""
        with self.assertRaises(ValidationError):
            self.env["mail.ice.server"].sudo().create(
                {
                    "server_type": "turns",
                    "uri": "10.0.0.5:99999?transport=tcp",
                    "username": "u",
                    "credential": "p",
                }
            )

    def test_internal_domain_allowed_when_configured(self):
        """Internal suffix ICE hosts are accepted."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        self.env["mail.ice.server"].sudo().create(
            {"server_type": "stun", "uri": "rtc.lan:3478"}
        )
        self.assertEqual(
            self.env["mail.ice.server"]._get_ice_servers()[0]["urls"],
            "stun:rtc.lan:3478",
        )

    def test_public_ice_rejected(self):
        """Public ICE hosts are rejected in intranet mode."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        self.env["mail.ice.server"].sudo().create(
            {"server_type": "stun", "uri": "public.example.com:19302"}
        )
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

    def test_turns_credentials_masked_in_diagnostics(self):
        """Diagnostics reveal only credential presence for TURNS records."""
        self.params.set_param("intranet_mail_rtc_ot.allow_custom_local_ice_servers", "True")
        self.env["mail.ice.server"].sudo().create(
            {
                "server_type": "turns",
                "uri": "10.0.0.5:443?transport=tcp",
                "username": "secret-user",
                "credential": "secret-password",
            }
        )
        wizard = self.env["intranet.rtc.diagnostic"].create({})
        safe = wizard._sanitize_ice_servers_for_display(
            self.env["mail.ice.server"]._get_ice_servers()
        )
        self.assertEqual(safe[0]["urls"], "turns:10.0.0.5:443?transport=tcp")
        self.assertTrue(safe[0]["has_username"])
        self.assertTrue(safe[0]["has_credential"])
        self.assertNotIn("secret-password", str(safe))
