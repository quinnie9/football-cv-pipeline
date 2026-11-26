#!/usr/bin/env python3
"""Smoke test for HU-0.2 — verify core dependencies import."""

from __future__ import annotations


def main() -> None:
    import cv2
    import ultralytics
    import supervision as sv
    import numpy as np
    import sklearn

    print("OpenCV      ", cv2.__version__)
    print("Ultralytics ", ultralytics.__version__)
    print("Supervision ", sv.__version__)
    print("NumPy       ", np.__version__)
    print("scikit-learn", sklearn.__version__)
    print("OK — smoke test passed")


if __name__ == "__main__":
    main()
