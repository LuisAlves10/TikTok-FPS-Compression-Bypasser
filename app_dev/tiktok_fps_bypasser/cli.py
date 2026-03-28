"""Command-line entry point."""

from __future__ import annotations

import argparse

from .secure_api import get_scale_factor_from_fps, get_video_fps, patch_mp4


def build_parser():
    parser = argparse.ArgumentParser(description="Apply the TikTok FPS metadata patch to an MP4 file.")
    parser.add_argument("input_file", help="Path to the input MP4 file")
    parser.add_argument("output_file", help="Path to the patched output MP4 file")
    parser.add_argument(
        "--fps",
        type=float,
        default=None,
        help="Original FPS of the video. If omitted, the tool tries to detect it automatically.",
    )
    parser.add_argument(
        "--scale-factor",
        type=float,
        default=None,
        help="Manual metadata scale factor. Overrides the FPS-based calculation when provided.",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    scale_factor = args.scale_factor
    if scale_factor is None:
        fps = args.fps if args.fps is not None else get_video_fps(args.input_file)
        scale_factor = get_scale_factor_from_fps(fps)
        if scale_factor is None:
            parser.error("Could not determine the original FPS. Use --fps or --scale-factor.")
        print(f"Detected FPS: {fps}")
        print(f"Scale factor: {scale_factor}")

    patch_mp4(args.input_file, args.output_file, scale_factor=scale_factor, log_func=print)
