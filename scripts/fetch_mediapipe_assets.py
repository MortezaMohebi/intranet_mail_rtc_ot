#!/usr/bin/env python3
"""Development helper to vendor MediaPipe Selfie Segmentation files.

This script is intentionally not used at runtime. Run it only on a development
machine with Internet access, then commit/copy the downloaded files into the
module before deploying to an intranet or airgapped Odoo server.
"""

from pathlib import Path
from urllib.request import urlretrieve

VERSION = "0.1.1675465747"
BASE_URL = f"https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation@{VERSION}"
FILES = [
    "selfie_segmentation.js",
    "selfie_segmentation.binarypb",
    "selfie_segmentation.tflite",
    "selfie_segmentation_landscape.tflite",
    "selfie_segmentation_solution_simd_wasm_bin.js",
    "selfie_segmentation_solution_simd_wasm_bin.wasm",
    "selfie_segmentation_solution_wasm_bin.js",
    "selfie_segmentation_solution_wasm_bin.wasm",
]


def main():
    """Download required MediaPipe files to the local module directory."""
    target_dir = Path(__file__).resolve().parents[1] / "static" / "lib" / "selfie_segmentation"
    target_dir.mkdir(parents=True, exist_ok=True)
    for file_name in FILES:
        url = f"{BASE_URL}/{file_name}"
        target = target_dir / file_name
        print(f"Downloading {url} -> {target}")
        urlretrieve(url, target)


if __name__ == "__main__":
    main()
