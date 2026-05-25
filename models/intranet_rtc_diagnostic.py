# -*- coding: utf-8 -*-
"""Diagnostics wizard for intranet RTC deployment validation."""

import json
import os
from pathlib import Path

from odoo import fields, models
from odoo.modules.module import get_module_path
from odoo.tools import config

from .intranet_rtc_policy import get_bool_param, is_allowed_sfu_url, is_enabled


class IntranetRtcDiagnostic(models.TransientModel):
    """Show safe diagnostics for administrators without exposing secrets."""

    _name = "intranet.rtc.diagnostic"
    _description = "Intranet RTC Diagnostic"

    name = fields.Char(default="Intranet RTC Diagnostics", readonly=True)
    intranet_mode_enabled = fields.Boolean(string="Intranet Mode", readonly=True)
    google_stun_fallback_blocked = fields.Boolean(string="Google STUN Blocked", readonly=True)
    twilio_rtc_disabled = fields.Boolean(string="Twilio RTC Disabled", readonly=True)
    sfu_allowed = fields.Boolean(string="SFU Allowed", readonly=True)
    sfu_url_configured = fields.Boolean(string="SFU URL Configured", readonly=True)
    sfu_url_is_internal = fields.Boolean(string="SFU URL Internal", readonly=True)
    local_mediapipe_assets_ok = fields.Boolean(string="Local Blur Assets OK", readonly=True)
    websocket_configured = fields.Boolean(string="WebSocket Port Configured", readonly=True)
    proxy_mode_enabled = fields.Boolean(string="Proxy Mode", readonly=True)
    effective_ice_server_count = fields.Integer(string="Effective ICE Server Count", readonly=True)
    gevent_or_longpolling_port = fields.Char(string="Gevent / Longpolling Port", readonly=True)
    missing_mediapipe_files = fields.Text(string="Missing MediaPipe Files", readonly=True)
    forbidden_runtime_refs = fields.Text(string="Forbidden Runtime References", readonly=True)
    status_json = fields.Text(string="Technical JSON", readonly=True)
    warning_text = fields.Text(string="Warnings", readonly=True)

    def _expected_mediapipe_files(self):
        """Return the expected MediaPipe Selfie Segmentation runtime files."""
        return [
            "selfie_segmentation.js",
            "selfie_segmentation.binarypb",
            "selfie_segmentation.tflite",
            "selfie_segmentation_landscape.tflite",
            "selfie_segmentation_solution_simd_wasm_bin.js",
            "selfie_segmentation_solution_simd_wasm_bin.wasm",
            "selfie_segmentation_solution_wasm_bin.js",
            "selfie_segmentation_solution_wasm_bin.wasm",
        ]

    def _runtime_forbidden_refs(self, module_path):
        """Return forbidden runtime references found outside docs and tests."""
        forbidden = (
            "stun1.l.google.com",
            "stun2.l.google.com",
            "cdn.jsdelivr.net",
            "tenor.googleapis.com",
            "translation.googleapis.com",
            "api.twilio.com",
        )
        ignored_parts = {
            "tests",
            "scripts",
            "README.md",
            "README_MEDIA_PIPE.md",
            "VERSION_HISTORY.md",
            "intranet_rtc_policy.py",
            "intranet_rtc_diagnostic.py",
        }
        hits = []
        for path in Path(module_path).rglob("*"):
            if not path.is_file() or path.suffix.lower() in {
                ".png",
                ".wasm",
                ".tflite",
                ".binarypb",
            }:
                continue
            rel = path.relative_to(module_path).as_posix()
            if any(part in rel for part in ignored_parts):
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for token in forbidden:
                if token in content:
                    hits.append(f"{rel}: {token}")
        return hits

    def _sanitize_ice_servers_for_display(self, ice_servers):
        """Return ICE server diagnostics without usernames or credentials."""
        safe_servers = []
        for server in ice_servers or []:
            if not isinstance(server, dict):
                continue
            safe_servers.append(
                {
                    "urls": server.get("urls"),
                    "has_username": bool(server.get("username")),
                    "has_credential": bool(server.get("credential")),
                }
            )
        return safe_servers

    def _build_diagnostics(self):
        """Build a safe diagnostics dictionary."""
        module_path = get_module_path("intranet_mail_rtc_ot")
        media_dir = os.path.join(module_path, "static", "lib", "selfie_segmentation")
        missing_media = [
            file_name
            for file_name in self._expected_mediapipe_files()
            if not os.path.exists(os.path.join(media_dir, file_name))
        ]
        sfu_url = self.env["ir.config_parameter"].sudo().get_param("mail.sfu_server_url") or ""
        effective_ice_servers = self.env["mail.ice.server"]._get_ice_servers() or []
        safe_ice_servers = self._sanitize_ice_servers_for_display(effective_ice_servers)
        gevent_port = config.get("gevent_port") or config.get("longpolling_port")
        forbidden_refs = self._runtime_forbidden_refs(module_path)
        diagnostics = {
            "intranet_mode_enabled": is_enabled(self.env),
            "effective_ice_server_count": len(effective_ice_servers),
            "effective_ice_servers_sent_to_clients_safe": safe_ice_servers,
            "google_stun_fallback_blocked": is_enabled(self.env),
            "twilio_rtc_disabled": get_bool_param(
                self.env,
                "intranet_mail_rtc_ot.disable_twilio_rtc",
                default=True,
            ),
            "sfu_allowed": bool(sfu_url and is_allowed_sfu_url(self.env, sfu_url)),
            "sfu_url_configured": bool(sfu_url),
            "sfu_url_is_internal": bool(sfu_url and is_allowed_sfu_url(self.env, sfu_url)),
            "local_mediapipe_assets_missing": missing_media,
            "cdn_references_in_runtime_code": forbidden_refs,
            "websocket_config_perspective": {
                "proxy_mode": bool(config.get("proxy_mode")),
                "gevent_or_longpolling_port": gevent_port,
                "appears_configured": bool(gevent_port),
            },
        }
        warnings = []
        if missing_media:
            warnings.append("Some local MediaPipe files are missing; blur will be disabled gracefully.")
        if not gevent_port:
            warnings.append("No gevent/longpolling port found in Odoo config; /websocket may not be usable.")
        if forbidden_refs:
            warnings.append("Forbidden runtime references were found in module runtime files.")
        if not effective_ice_servers:
            warnings.append(
                "ICE servers are empty. Direct host-candidate P2P may fail across NAT/firewalls; use local TURN or local SFU if required."
            )
        return diagnostics, "\n".join(warnings)

    def action_run_diagnostics(self):
        """Run diagnostics and update this wizard."""
        for wizard in self:
            diagnostics, warnings = wizard._build_diagnostics()
            websocket = diagnostics["websocket_config_perspective"]
            missing_media = diagnostics["local_mediapipe_assets_missing"]
            forbidden_refs = diagnostics["cdn_references_in_runtime_code"]
            wizard.write(
                {
                    "intranet_mode_enabled": diagnostics["intranet_mode_enabled"],
                    "google_stun_fallback_blocked": diagnostics["google_stun_fallback_blocked"],
                    "twilio_rtc_disabled": diagnostics["twilio_rtc_disabled"],
                    "sfu_allowed": diagnostics["sfu_allowed"],
                    "sfu_url_configured": diagnostics["sfu_url_configured"],
                    "sfu_url_is_internal": diagnostics["sfu_url_is_internal"],
                    "local_mediapipe_assets_ok": not missing_media,
                    "websocket_configured": websocket["appears_configured"],
                    "proxy_mode_enabled": websocket["proxy_mode"],
                    "effective_ice_server_count": diagnostics["effective_ice_server_count"],
                    "gevent_or_longpolling_port": str(websocket["gevent_or_longpolling_port"] or ""),
                    "missing_mediapipe_files": "\n".join(missing_media),
                    "forbidden_runtime_refs": "\n".join(forbidden_refs),
                    "status_json": json.dumps(diagnostics, indent=2, ensure_ascii=False),
                    "warning_text": warnings,
                }
            )
        return {
            "type": "ir.actions.act_window",
            "name": "Intranet RTC Diagnostics",
            "res_model": "intranet.rtc.diagnostic",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            "view_id": self.env.ref("intranet_mail_rtc_ot.intranet_rtc_diagnostic_view_form").id,
        }
