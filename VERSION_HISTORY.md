
## 18.0.1.0.1

- Exported `post_init_hook` and `uninstall_hook` from module root for Odoo installer compatibility.
- Removed the erroneous zero-byte `selfie_segmentation_solution_simd_wasm_bin.data` asset from the package.
- Updated MediaPipe diagnostics and downloader to require only files actually requested by Odoo 18's bundled Selfie Segmentation runtime.
- Repacked ZIP with POSIX-style paths for safer deployment on Linux servers.

# Version History

## 18.0.1.0.0

- Initial production-oriented intranet RTC hardening module.
- Backend explicit empty ICE server handling.
- Local-only ICE validation.
- Twilio and SFU blocking policy.
- Frontend RTC/P2P public ICE fallback removal.
- Local MediaPipe blur asset path replacement.
- External Discuss extras disabling.
- Settings UI, diagnostics, security groups, hooks, and tests.
## 18.0.1.0.2

- Added explicit Odoo JavaScript aliases for the three replaced Mail RTC modules.
- Fixed the relative `./call_actions` import inside the RTC service replacement.
- This prevents missing module definitions and restores `Rtc.register()` execution during backend asset startup.

## 18.0.1.0.3

- Add backend debug logging for RTC join, ICE sanitization, local-only SFU blocking, and effective ICE server counts.
- Add frontend debug logging for secure context checks, media permission failures, ICE candidates, ICE gathering, connection state, data channel state, offer/answer signaling, and remote track reception.
- Frontend logs are silent by default and can be enabled per browser with `localStorage.setItem("intranet_mail_rtc_ot.debug", "1")`.
- Add extra guidance for direct host-candidate P2P limitations on routed intranet/VLAN/firewall networks.

## 18.0.1.0.4

- Refactored Discuss settings UI into clean Odoo 18 settings blocks.
- Replaced the crowded diagnostic button with a compact Open Diagnostics action.
- Moved diagnostics from the generic Technical menu to Discuss > Configuration.
- Redesigned diagnostics form with grouped status fields, warnings, and a technical JSON tab.
- Sanitized diagnostic ICE output to avoid exposing TURN usernames or credentials.

## 18.0.1.0.6

- Fixed the Direct P2P setting so unchecked values persist from the Settings UI.
- Renamed the setting to **Allow Direct P2P Fallback** for clearer meaning.
- When Direct P2P Fallback is disabled and no local ICE/SFU transport exists, calls are blocked with an actionable error instead of silently using host-candidate P2P.
- Diagnostics now show whether Direct P2P Fallback is enabled and warn when no usable local transport is available.

## 18.0.1.0.5

- Expanded README with a practical user and administrator guide.
- Documented how peer-to-peer WebRTC works in intranet mode.
- Explained why same-LAN users can hear each other while home/remote users may need VPN, local TURN, or local SFU.
- Added setup guidance for direct P2P, local TURN, local SFU, browser permissions, diagnostics, and troubleshooting.

## 18.0.1.0.7

- Add full `turns:` ICE server support.
- Support secure TURN over TLS for locked networks.
- Support TURNS over TCP 443.
- Prevent double-prefix ICE URL generation.
- Treat `turns:` as a TURN-capable relay URL in frontend checks.
- Improve safe diagnostics for TURNS records.
- Preserve direct P2P toggle behavior from 18.0.1.0.6.
- Preserve blocked external fallback behavior.

## 18.0.1.0.8

- Fix module upgrade failure caused by duplicate `ir.config_parameter` XML records.
- Stop loading default config parameters through XML records.
- Keep safe defaults managed by `post_init_hook` and `res.config.settings` instead.
- Preserve existing user-configured values during upgrades.
- Preserve all `turns:` support from 18.0.1.0.7.
