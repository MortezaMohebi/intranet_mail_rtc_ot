# MediaPipe Selfie Segmentation local assets

Package: `@mediapipe/selfie_segmentation`

Target version used by Odoo 18 blur integration: `0.1.x`; latest 0.1 package observed during development: `0.1.1675465747`.

Local runtime path:

`/intranet_mail_rtc_ot/static/lib/selfie_segmentation/`

Expected runtime files:

- `selfie_segmentation.js`
- `selfie_segmentation.binarypb`
- `selfie_segmentation.tflite`
- `selfie_segmentation_landscape.tflite`
- `selfie_segmentation_solution_simd_wasm_bin.js`
- `selfie_segmentation_solution_simd_wasm_bin.wasm`
- `selfie_segmentation_solution_wasm_bin.js`
- `selfie_segmentation_solution_wasm_bin.wasm`

Source used during development:

- jsDelivr package listing for `@mediapipe/selfie_segmentation`
- GitHub mirror `streamfog/mediapipe-selfieseg`

License notes:

- MediaPipe JavaScript solution files are distributed under Apache-2.0 notices from Google/MediaPipe.
- Keep the upstream copyright/license comments inside vendored JavaScript files.

Runtime confirmation:

- `blur_manager_local.js` uses only `/intranet_mail_rtc_ot/static/lib/selfie_segmentation/${file}`.
- It never constructs a CDN URL.
- If any local file is missing, background blur is disabled gracefully and normal camera/audio calls continue.

Packaging note for this generated artifact:

- The uploaded Odoo `mail.zip` contained `selfie_segmentation.js` only.
- `selfie_segmentation.binarypb` is included because it was available as a small public source file.
- The large `.tflite`, `.wasm`, `.data`, and wasm helper `.js` files must be copied into this folder from the exact package version before enabling blur in production.
- Run the diagnostics wizard after copying them; it reports missing files explicitly.
