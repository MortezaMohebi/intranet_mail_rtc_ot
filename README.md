# intranet_mail_rtc_ot

Production-oriented Odoo 18 addon for running Discuss audio/video calls in locked intranet, airgapped, or Internet-blocked environments.

The module is designed for organizations that want Odoo Discuss calls to work without silently using public Google STUN, Twilio TURN, public SFU, CDN assets, or other external runtime services.

## User guide

### What this module does for users

When users start an Odoo Discuss audio or video call, Odoo normally coordinates the call through Discuss and the browser's WebRTC engine. Odoo is responsible for signaling: joining the call, notifying other members, exchanging session information, and keeping Discuss state synchronized.

The actual audio/video media does **not** normally pass through the Odoo HTTP server. In peer-to-peer mode, the browsers try to send media directly to each other.

This module keeps that behavior, but makes it intranet-safe:

- It prevents fallback to Google STUN servers.
- It prevents Twilio RTC usage in intranet mode.
- It prevents public SFU fallback.
- It serves MediaPipe background-blur assets locally from Odoo instead of a CDN.
- It disables selected external Discuss extras, such as external GIF, translation, push, and link preview calls when configured.
- It sends an explicit empty ICE server list when no approved local ICE/TURN server exists.

### What users should expect

Users inside the same office LAN usually work immediately if their browsers, microphones, cameras, and firewalls allow WebRTC.

Users in different networks, home networks, mobile networks, or separate NAT environments may join the call UI but fail to hear or see others unless the network provides one of these:

- Direct routed connectivity between all participants.
- A company VPN that routes client-to-client traffic correctly.
- A self-hosted local/company TURN server.
- A self-hosted local/company SFU.

This is normal WebRTC behavior. The module intentionally refuses to solve NAT traversal by using Google, Twilio, or public relay services.

### Example: why office users can hear each other but a home user cannot

If the boss and product manager are both on the office LAN, their browsers can often connect directly:

```text
Boss PC  <---- direct LAN WebRTC media ---->  Product Manager PC
```

If a third user joins from home, that user is usually behind a different router, firewall, and NAT:

```text
Home PC  <---- NAT/firewall boundary ---->  Office LAN PCs
```

With `iceServers: []`, there is no public STUN/TURN relay. The home browser can still connect to Odoo for Discuss signaling, but the media path may fail because the home PC and office PCs cannot directly UDP-connect to each other.

For this case, use a company VPN, a self-hosted TURN server, or a self-hosted SFU.

## Network requirements

### Same LAN or same routable intranet

This is the simplest supported case.

Requirements:

- All users can open Odoo.
- Websocket/bus works.
- Browsers can access microphone/camera.
- Client devices can directly reach each other over the network.
- Endpoint firewalls do not block WebRTC UDP traffic.
- Wi-Fi client isolation is disabled.

Typical example:

```text
Client A: 192.168.10.50
Client B: 192.168.10.60
Odoo:     192.168.10.101:8069
```

### Different VLANs or routed office networks

This can work, but only if the network routes traffic between clients.

Example:

```text
Client A: 192.168.10.50
Client B: 192.168.20.60
```

Requirements:

- Routing between VLANs is allowed.
- ACLs/firewalls allow client-to-client UDP media traffic.
- No network isolation blocks peer-to-peer traffic.

### Home users, remote users, or Internet-separated users

Plain direct peer-to-peer usually fails here unless a VPN or relay is used.

Recommended options:

1. Connect remote users through the company VPN and route client-to-client traffic.
2. Deploy a self-hosted TURN server and configure it as an allowed local ICE server.
3. Deploy a self-hosted SFU for larger or more controlled meetings.

## Admin guide

### Safe default mode

After installation, the module uses safe intranet defaults:

- Intranet RTC mode: enabled
- Force empty ICE servers: enabled
- Custom local ICE servers: disabled
- Local SFU: disabled
- Twilio RTC: disabled
- External push/GIF/translate/link preview: disabled
- Local blur assets: enabled

This means calls use direct browser-to-browser host candidates only.

### Settings location

Go to:

```text
Settings → Discuss
```

Find the Intranet RTC settings blocks:

- Intranet RTC
- Intranet RTC: Call Transport
- Intranet RTC: Blocked External Services

Diagnostics are available from:

```text
Discuss → Configuration → Intranet RTC Diagnostics
```

### Direct P2P configuration

Use this for fully local office users.

Recommended settings:

- Enable Intranet RTC Mode: enabled
- Force Empty ICE Servers: enabled
- Allow Custom Local ICE Servers: disabled
- Allow Local SFU: disabled
- Disable Twilio RTC: enabled
- Use Local Background Blur Assets: enabled

Expected browser result in `chrome://webrtc-internals`:

```text
iceServers: []
```

### Local TURN configuration

Use this when users are on different subnets, VPNs, home networks, or when strict endpoint firewalls prevent direct P2P.

Deploy your own TURN server, for example `coturn`, inside your controlled infrastructure. This module does not provide TURN itself; it only allows Odoo to send approved local/internal TURN records to the browser.

Recommended settings:

- Enable Intranet RTC Mode: enabled
- Force Empty ICE Servers: enabled
- Allow Custom Local ICE Servers: enabled
- Disable Twilio RTC: enabled

Then configure Odoo's `mail.ice.server` records with your own TURN URI, for example:

```text
turn:turn.company.internal:3478?transport=udp
turns:turn.company.internal:5349?transport=tcp
```

Allowed TURN/STUN hosts must be local/private/internal. The module allows:

- Private IPv4 hosts such as `10.x.x.x`, `172.16.x.x` to `172.31.x.x`, `192.168.x.x`
- Loopback hosts such as `127.0.0.1` and `localhost`
- Private/internal suffixes such as `.local`, `.lan`, `.internal`, `.intra`
- Additional suffixes configured in **Allowed Internal ICE Host Suffixes**

If your self-hosted TURN server must be reached by remote users through a company-owned public DNS name, prefer a hostname such as:

```text
turn.company.example
```

Then add the owned suffix to **Allowed Internal ICE Host Suffixes**, for example:

```text
.company.example
```

Do not use Google, Twilio, or random public STUN/TURN services.

### Local SFU configuration

Use SFU when you need better multi-person meeting behavior. In P2P, every participant sends media to every other participant, which becomes heavy with multiple users.

Use local SFU only when:

- The SFU is self-hosted or company-hosted.
- Its URL is explicitly internal/local or explicitly allowed.
- It does not depend on public Odoo/Twilio/third-party infrastructure.

Recommended settings:

- Allow Local SFU: enabled
- Allowed SFU Hosts: set to the local/internal SFU hostname or suffix

If no SFU is configured or allowed, the module stays in peer-to-peer mode.

## Browser and device requirements

### HTTPS and secure context

Browsers restrict microphone and camera access to secure contexts. `http://localhost` and `http://127.0.0.1` are treated specially, but `http://192.168.x.x` may not be accepted by all browsers or policies.

For real intranet deployment, prefer:

```text
https://odoo.company.internal
```

instead of:

```text
http://192.168.10.101:8069
```

### Microphone and camera checks

If a user can join the call but cannot transmit audio, check browser and operating system permissions.

In Chrome DevTools Console:

```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
    .then((stream) => {
        console.log("MIC OK:", stream.getAudioTracks()[0].label);
        stream.getTracks().forEach((track) => track.stop());
    })
    .catch((error) => {
        console.error("MIC FAILED:", error.name, error.message);
    });
```

Common causes:

- No microphone device is installed.
- Browser microphone permission is blocked.
- Windows/macOS privacy settings block microphone access.
- Another app is holding the microphone.
- The page is not a secure context.

## Diagnostics guide

Run diagnostics from:

```text
Discuss → Configuration → Intranet RTC Diagnostics
```

The diagnostics show:

- Whether intranet mode is enabled.
- Effective ICE servers sent to clients.
- Whether Google STUN fallback is blocked.
- Whether Twilio RTC is disabled.
- SFU policy status.
- Whether local MediaPipe files exist.
- Whether runtime CDN references remain.
- Websocket/gevent configuration perspective.

### Browser debug logs

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

The frontend logger reports:

- Secure-context status
- Media API availability
- Media permission failures
- Selected ICE server count
- ICE candidates
- ICE gathering state
- ICE connection state
- Data-channel state
- Offer/answer signaling
- Remote track reception

It does not log TURN usernames or credentials.

### Backend debug logs

Backend logs are controlled by the module setting:

```text
Debug RTC Logs
```

When enabled, Odoo logs:

- RTC join flow
- Effective ICE server count
- ICE filtering decisions
- SFU policy decisions

Credentials are masked.

## Verification checklist

In browser DevTools Network and `chrome://webrtc-internals`, verify:

- No request or ICE server entry points to `stun1.l.google.com`.
- No request or ICE server entry points to `stun2.l.google.com`.
- No request points to `cdn.jsdelivr.net` at runtime.
- No request points to `googleapis.com` or `twilio.com` for RTC.
- MediaPipe files load from `/intranet_mail_rtc_ot/static/lib/selfie_segmentation/`.
- `iceServers` is empty in direct P2P mode or contains only approved local/internal TURN/STUN servers.

## Troubleshooting matrix

| Symptom | Likely cause | Fix |
|---|---|---|
| Office users hear each other, home user cannot hear anyone | Home user is behind NAT/firewall and cannot direct P2P to office clients | Use VPN, local TURN, or local SFU |
| Call opens, but no one hears audio | Microphone permission/device problem or blocked media tracks | Test `getUserMedia`, check OS/browser permissions |
| Call opens, but ICE state becomes `failed` | Network cannot route peer-to-peer UDP | Use local TURN/SFU or fix routing/firewall |
| Same Wi-Fi users cannot hear each other | Wi-Fi client isolation or endpoint firewall | Disable client isolation, allow local UDP |
| DevTools shows Google STUN | Module not installed/updated or another asset overrides RTC code | Update module, clear assets, restart Odoo, inspect active assets |
| Background blur requests CDN | Local MediaPipe assets missing or old asset bundle cached | Install full offline package, update module, clear browser/Odoo assets |

## What this module changes

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

## MediaPipe background blur assets

The full offline package must contain these files under:

```text
intranet_mail_rtc_ot/static/lib/selfie_segmentation/
```

Expected runtime files:

```text
selfie_segmentation.js
selfie_segmentation.binarypb
selfie_segmentation.tflite
selfie_segmentation_landscape.tflite
selfie_segmentation_solution_simd_wasm_bin.js
selfie_segmentation_solution_simd_wasm_bin.wasm
selfie_segmentation_solution_wasm_bin.js
selfie_segmentation_solution_wasm_bin.wasm
```

If these files are missing, calls should still work, but background blur will be disabled or degraded and diagnostics will report the missing files.


### Direct P2P Fallback setting

The setting **Allow Direct P2P Fallback** controls what happens when intranet mode is enabled but no validated local TURN/STUN/SFU transport is available.

- Enabled: Odoo sends `iceServers: []`. Browsers try direct host-candidate P2P only. This works for same-LAN or fully routed intranet clients.
- Disabled: Odoo refuses to start the RTC call unless a validated local ICE server or allowed local SFU is configured. This is useful when you do not want remote/home users to enter a call that cannot carry media.

Disabling this setting does not re-enable Google STUN or Twilio. External fallbacks remain blocked.


## Secure TURN over TLS (`turns:`)

Version 18.0.1.0.7 supports Odoo ICE server records with the `turns:` type. Use this when remote or home users cannot directly reach office clients, but you still need a self-hosted relay instead of Google/Twilio/public services.

Recommended TURNS record for TCP 443:

```text
Type: turns:
URI: turn.example.com:443?transport=tcp
Username: your configured TURN username
Credential: your configured TURN password
```

Enter only the URI part in Odoo. Do not include the `turns:` prefix inside the URI field. If a full URL is pasted by mistake, the module normalizes it before generating the browser ICE URL, preventing invalid values such as `turns:turns:...`.

For strict relay-only operation, set **ICE Transport Policy** to **Relay only** after a valid local TURN/TURNS server is configured. Leave it as **All candidates** for normal backward-compatible intranet behavior.

Diagnostics intentionally show only safe metadata:

```json
{
  "urls": "turns:turn.example.com:443?transport=tcp",
  "has_username": true,
  "has_credential": true
}
```

The real credential is sent only to the browser as part of WebRTC ICE configuration and is never displayed in diagnostics, chatter, or debug logs. Rotate TURN credentials if they were copied into browser screenshots, tickets, or shared logs during testing.
