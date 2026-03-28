"""Loader for the compiled secure backend."""

from __future__ import annotations

import importlib


BACKEND_NAME = "cython"

try:
    secure_core = importlib.import_module(".secure_core", __package__)
except ImportError:
    secure_core = importlib.import_module(".secure_fallback", __package__)
    BACKEND_NAME = "python"


get_scale_factor_from_fps = secure_core.get_scale_factor_from_fps
get_video_fps = secure_core.get_video_fps
patch_atom = secure_core.patch_atom
patch_mp4 = secure_core.patch_mp4
