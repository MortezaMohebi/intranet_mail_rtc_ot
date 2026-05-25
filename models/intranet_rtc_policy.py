# -*- coding: utf-8 -*-
"""Shared policy helpers for intranet-only RTC behavior."""

import ipaddress
import logging
import re
from urllib.parse import urlparse

_logger = logging.getLogger(__name__)

FORBIDDEN_HOST_FRAGMENTS = (
    "stun1.l.google.com",
    "stun2.l.google.com",
    "google.com",
    "googleapis.com",
    "twilio.com",
)

DEFAULT_INTERNAL_SUFFIXES = (".local", ".lan", ".internal", ".intra")
ICE_SCHEMES = ("stun:", "stuns:", "turn:", "turns:")


def get_bool_param(env, key, default=False):
    """Return a boolean configuration parameter value."""
    value = env["ir.config_parameter"].sudo().get_param(key)
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def get_csv_param(env, key, default=""):
    """Return a normalized list from a comma or newline separated config parameter."""
    raw_value = env["ir.config_parameter"].sudo().get_param(key, default) or ""
    items = re.split(r"[,\n\r]+", raw_value)
    return [item.strip().lower() for item in items if item.strip()]


def is_enabled(env):
    """Return whether intranet RTC policy is enabled."""
    return get_bool_param(env, "intranet_mail_rtc_ot.enabled", default=True)




def is_direct_p2p_fallback_enabled(env):
    """Return whether host-candidate P2P fallback is allowed without local ICE/SFU."""
    return get_bool_param(
        env,
        "intranet_mail_rtc_ot.force_empty_ice_servers",
        default=True,
    )

def is_debug_enabled(env):
    """Return whether verbose RTC debug logs are enabled."""
    return get_bool_param(env, "intranet_mail_rtc_ot.debug_rtc_logs", default=False)


def debug_log(env, message, *args):
    """Emit a debug log only when RTC debug logging is enabled."""
    if is_debug_enabled(env):
        _logger.info("[intranet_mail_rtc_ot] " + message, *args)


def _is_forbidden_host(host):
    """Return whether the host belongs to a known public RTC provider."""
    normalized = (host or "").strip().lower().rstrip(".")
    return any(
        normalized == fragment or normalized.endswith("." + fragment)
        for fragment in FORBIDDEN_HOST_FRAGMENTS
    )


def _extract_host_from_ice_url(ice_url):
    """Extract a safe host string from a STUN/TURN URI."""
    value = str(ice_url or "").strip()
    lower = value.lower()
    if not any(lower.startswith(scheme) for scheme in ICE_SCHEMES):
        return ""
    remainder = value.split(":", 1)[1].lstrip("/")
    remainder = remainder.split("?", 1)[0].split("/", 1)[0]
    if "@" in remainder:
        remainder = remainder.rsplit("@", 1)[1]
    if remainder.startswith("[") and "]" in remainder:
        return remainder[1:remainder.index("]")].lower()
    return remainder.split(":", 1)[0].lower().rstrip(".")


def _extract_host_from_url(url):
    """Extract a lowercase host from a regular URL."""
    parsed = urlparse(str(url or "").strip())
    return (parsed.hostname or "").lower().rstrip(".")


def _is_private_ip(host):
    """Return whether host is a private or loopback IP address."""
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    if address.version == 4:
        return address.is_private or address.is_loopback
    return address.is_private or address.is_loopback or address.is_link_local


def is_internal_host(env, host, *, extra_suffix_key=None, exact_hosts_key=None):
    """Return whether a host is explicitly local/private/internal."""
    normalized = (host or "").strip().lower().rstrip(".")
    if not normalized or _is_forbidden_host(normalized):
        return False
    if normalized == "localhost" or _is_private_ip(normalized):
        return True

    suffixes = list(DEFAULT_INTERNAL_SUFFIXES)
    if extra_suffix_key:
        suffixes.extend(get_csv_param(env, extra_suffix_key))
    if any(normalized.endswith(suffix.lower().lstrip("*")) for suffix in suffixes):
        return True

    if exact_hosts_key:
        allowed_hosts = get_csv_param(env, exact_hosts_key)
        for allowed_host in allowed_hosts:
            allowed_host = allowed_host.rstrip(".")
            if normalized == allowed_host or normalized.endswith("." + allowed_host):
                return True
    return False


def mask_ice_server(server):
    """Return a log-safe copy of an ICE server without credentials."""
    if not isinstance(server, dict):
        return {"invalid": type(server).__name__}
    clean = {key: value for key, value in server.items() if key not in {"username", "credential"}}
    if "username" in server:
        clean["username"] = "***"
    if "credential" in server:
        clean["credential"] = "***"
    return clean


def sanitize_ice_servers(env, ice_servers):
    """Filter ICE servers so only private/local hosts remain in intranet mode."""
    if not is_enabled(env):
        return ice_servers or []
    if not get_bool_param(env, "intranet_mail_rtc_ot.allow_custom_local_ice_servers", default=False):
        if is_direct_p2p_fallback_enabled(env):
            debug_log(
                env,
                "ICE policy: custom local ICE servers disabled; direct P2P fallback will use empty iceServers list.",
            )
        else:
            debug_log(
                env,
                "ICE policy: custom local ICE servers disabled and direct P2P fallback disabled; no ICE servers are available.",
            )
        return []
    debug_log(env, "ICE policy: sanitizing %s configured ICE server entries.", len(ice_servers or []))
    sanitized = []
    for server in ice_servers or []:
        if not isinstance(server, dict):
            _logger.warning("Rejected malformed ICE server entry: %s", type(server).__name__)
            continue
        raw_urls = server.get("urls") or server.get("url") or []
        urls = raw_urls if isinstance(raw_urls, (list, tuple)) else [raw_urls]
        valid_urls = []
        rejected_hosts = []
        for ice_url in urls:
            host = _extract_host_from_ice_url(ice_url)
            if is_internal_host(
                env,
                host,
                extra_suffix_key="intranet_mail_rtc_ot.allowed_ice_host_suffixes",
            ):
                debug_log(env, "ICE policy: accepted local ICE host '%s'.", host)
                valid_urls.append(ice_url)
            else:
                debug_log(env, "ICE policy: rejected non-local ICE host '%s'.", host or "<empty>")
                rejected_hosts.append(host or "<empty>")
        if not valid_urls:
            _logger.warning(
                "Rejected ICE server outside intranet policy: %s; hosts=%s",
                mask_ice_server(server),
                sorted(set(rejected_hosts)),
            )
            continue
        clean_server = dict(server)
        clean_server.pop("url", None)
        clean_server["urls"] = valid_urls[0] if isinstance(raw_urls, str) else valid_urls
        sanitized.append(clean_server)
    debug_log(env, "ICE policy: sanitized ICE server count=%s.", len(sanitized))
    return sanitized


def is_allowed_sfu_url(env, sfu_url):
    """Return whether the configured SFU URL is allowed by intranet settings."""
    if not is_enabled(env):
        return True
    if not get_bool_param(env, "intranet_mail_rtc_ot.allow_local_sfu", default=False):
        debug_log(env, "SFU policy: local SFU support disabled by configuration.")
        return False
    host = _extract_host_from_url(sfu_url)
    allowed = is_internal_host(
        env,
        host,
        exact_hosts_key="intranet_mail_rtc_ot.allowed_sfu_hosts",
        extra_suffix_key="intranet_mail_rtc_ot.allowed_ice_host_suffixes",
    )
    debug_log(env, "SFU policy: host='%s' allowed=%s.", host or "<empty>", allowed)
    return allowed
