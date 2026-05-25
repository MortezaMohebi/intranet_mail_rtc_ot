
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
