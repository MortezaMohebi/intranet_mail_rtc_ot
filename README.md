# intranet_mail_rtc_ot

Production-oriented Odoo 18 addon for running Discuss audio/video calls in locked intranet, airgapped, or Internet-blocked environments.

## What it changes

- Backend RTC join responses always send an explicit `iceServers: []` when intranet mode is enabled and no approved local ICE server exists.
- Odoo's Twilio RTC token flow is bypassed in intranet mode.
- SFU is blocked unless explicitly enabled and configured with local/internal hosts.
- Frontend RTC and P2P defaults are changed from public STUN fallback to an empty ICE list.
- Runtime Google/Twilio ICE URLs are sanitized defensively if another addon injects them.
- Background blur `locateFile` points to `/intranet_mail_rtc_ot/static/lib/selfie_segmentation/`.
- Tenor GIF, Google Translate, external Web Push, and external link preview fetching are disabled by default.
- Diagnostics report missing MediaPipe runtime files, effective ICE servers, SFU status, and websocket-related Odoo config.

## Important WebRTC note

This module does not disable WebRTC ICE itself. Browsers always use ICE internally. The module prevents external ICE servers and sends an explicit empty ICE server list for direct host-candidate peer-to-peer mode. Networks with NAT/firewalls may still require a local TURN server or a local SFU.

## Configuration

Go to **Settings → Discuss → Intranet RTC Mode** or **Settings → Technical → Intranet RTC**.

Safe defaults are enabled on install:

- Intranet RTC mode: enabled
- Force empty ICE servers: enabled
- Custom local ICE servers: disabled
- Local SFU: disabled
- Twilio RTC: disabled
- External push/GIF/translate/link preview: disabled
- Local blur assets: enabled

## Browser verification

In DevTools Network and `chrome://webrtc-internals`, verify:

- No public STUN/TURN/SFU endpoints are used.
- ICE server list is empty unless local ICE servers are explicitly configured.
- MediaPipe files are requested from `/intranet_mail_rtc_ot/static/lib/selfie_segmentation/`.

## Limitation of direct P2P

Empty ICE servers means the browser can still gather local host candidates. This works only when participants can route directly to each other. If direct P2P fails, configure a local TURN server or a local SFU and add its host to the allowlist.

## RTC Debug Logging

Frontend RTC logs are disabled by default. Enable them only while diagnosing a call from the browser console, then reload the page:

```javascript
localStorage.setItem("intranet_mail_rtc_ot.debug", "1");
location.reload();
```

Disable them after testing:

```javascript
localStorage.removeItem("intranet_mail_rtc_ot.debug");
location.reload();
```

The frontend logger reports secure-context status, media API availability, selected ICE server count, local ICE candidates, ICE gathering state, connection state, data-channel state, offer/answer signaling, and received remote tracks. It does not log TURN usernames or credentials.

Backend logs are controlled by the module setting **Debug RTC Logs**. When enabled, Odoo logs the RTC join flow, effective ICE server count, ICE filtering decisions, and SFU policy decisions without exposing credentials.

### Important direct P2P note

With `iceServers: []`, WebRTC can only use direct host candidates. If clients are separated by VLANs, routed segments, NAT, endpoint firewall rules, or browser policies, calls may start but no media will flow. In that case, deploy an explicitly configured local TURN server or local SFU; this module intentionally will not fall back to Google, Twilio, or public STUN/TURN.

Also prefer HTTPS even on private IP addresses. Modern browsers restrict camera/microphone APIs to secure contexts, except limited localhost exceptions. If testing with `http://192.168.x.x`, the debug logger will show whether `window.isSecureContext` and `navigator.mediaDevices` are available.


## 18.0.1.0.4 UI Update

The settings are now split into professional Odoo settings blocks under Settings > Discuss, and diagnostics are available under Discuss > Configuration > Intranet RTC Diagnostics.
