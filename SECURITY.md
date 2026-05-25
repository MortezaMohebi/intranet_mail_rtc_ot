# Security notes

- TURN credentials are never logged by this module. Rejected ICE server logs mask `username` and `credential`.
- Normal users can use Discuss calls but cannot edit intranet RTC settings.
- Only system/technical users can run diagnostics.
- In intranet mode, Twilio RTC, external Web Push, Tenor GIF, Google Translate, and external link preview fetching are disabled by default.
- SFU usage is denied unless the host is explicitly local/internal and allowed by configuration.
- This module does not monkey-patch global browser WebRTC APIs.
