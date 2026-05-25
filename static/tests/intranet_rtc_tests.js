/** @odoo-module **/

import { PeerToPeer } from "@mail/discuss/call/common/peer_to_peer";
import { BlurManager } from "@mail/discuss/call/common/blur_manager";

QUnit.module("intranet_mail_rtc_ot", () => {
    QUnit.test("PeerToPeer.connect defaults to empty ICE servers", (assert) => {
        assert.expect(1);
        const p2p = new PeerToPeer({ enableStreaming: false });
        p2p.connect(1, 1);
        assert.deepEqual(p2p._iceServers, []);
    });

    QUnit.test("PeerToPeer.connect sanitizes public ICE providers", (assert) => {
        assert.expect(1);
        const p2p = new PeerToPeer({ enableStreaming: false });
        p2p.connect(1, 1, {
            iceServers: [{ urls: ["stun:provider.google.invalid:19302"] }],
        });
        assert.deepEqual(p2p._iceServers, []);
    });

    QUnit.test("PeerToPeer.connect preserves explicit empty ICE list", (assert) => {
        assert.expect(1);
        const p2p = new PeerToPeer({ enableStreaming: false });
        p2p.connect(1, 1, { iceServers: [] });
        assert.deepEqual(p2p._iceServers, []);
    });

    QUnit.test("PeerToPeer.connect preserves local ICE list", (assert) => {
        assert.expect(1);
        const localIce = [{ urls: ["turn:10.10.0.10:3478"], username: "u", credential: "p" }];
        const p2p = new PeerToPeer({ enableStreaming: false });
        p2p.connect(1, 1, { iceServers: localIce });
        assert.deepEqual(p2p._iceServers, localIce);
    });

    QUnit.test("BlurManager uses local Odoo MediaPipe URL", (assert) => {
        assert.expect(1);
        const original = window.SelfieSegmentation;
        let locatedUrl;
        window.SelfieSegmentation = class FakeSelfieSegmentation {
            constructor({ locateFile }) {
                locatedUrl = locateFile("selfie_segmentation.binarypb");
            }
            setOptions() {}
            onResults() {}
            reset() {}
        };
        const stream = new MediaStream();
        const manager = new BlurManager(stream);
        manager.close();
        window.SelfieSegmentation = original;
        assert.strictEqual(
            locatedUrl,
            "/intranet_mail_rtc_ot/static/lib/selfie_segmentation/selfie_segmentation.binarypb"
        );
    });
});
