# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: nonecheck=False

import os
import subprocess


def get_video_fps(video_path):
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=r_frame_rate",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        if "/" in out:
            numerator, denominator = map(int, out.split("/"))
            return round(numerator / denominator, 2) if denominator else None
        return float(out)
    except Exception:
        return None


def get_scale_factor_from_fps(fps):
    if fps is None or fps <= 0:
        return None
    return 30 / fps


def patch_atom(atom_name, bytearray data, scale_factor=None, log_func=None):
    cdef Py_ssize_t start = 0
    cdef Py_ssize_t found
    cdef Py_ssize_t header_offset
    cdef int count = 0
    cdef int box_size
    cdef int version
    cdef int timescale_offset
    cdef int duration_offset
    cdef unsigned int old_timescale
    cdef unsigned long long old_duration
    cdef unsigned int new_timescale
    cdef bytes atom_bytes = atom_name.encode("utf-8")

    while True:
        found = data.find(atom_bytes, start)
        if found == -1:
            break

        header_offset = found - 4
        if header_offset < 0:
            start = found + 4
            continue

        box_size = int.from_bytes(data[header_offset : header_offset + 4], "big")
        if box_size < 8:
            start = found + 4
            continue

        version = data[header_offset + 8]

        try:
            if version == 0:
                timescale_offset = header_offset + 20
                duration_offset = header_offset + 24
                if duration_offset + 4 > header_offset + box_size:
                    start = found + 4
                    continue

                old_timescale = int.from_bytes(data[timescale_offset : timescale_offset + 4], "big")
                old_duration = int.from_bytes(data[duration_offset : duration_offset + 4], "big")
                if old_timescale == 0 or scale_factor is None:
                    start = found + 4
                    continue

                new_timescale = max(1, int(old_timescale * scale_factor))
                data[timescale_offset : timescale_offset + 4] = new_timescale.to_bytes(4, "big")

                if log_func is not None:
                    log_func(
                        f"Patched {atom_name} | timescale {old_timescale} -> {new_timescale} | duration kept {old_duration}"
                    )
                count += 1

            elif version == 1:
                timescale_offset = header_offset + 28
                duration_offset = header_offset + 32
                if duration_offset + 8 > header_offset + box_size:
                    start = found + 4
                    continue

                old_timescale = int.from_bytes(data[timescale_offset : timescale_offset + 4], "big")
                old_duration = int.from_bytes(data[duration_offset : duration_offset + 8], "big")
                if old_timescale == 0 or scale_factor is None:
                    start = found + 4
                    continue

                new_timescale = max(1, int(old_timescale * scale_factor))
                data[timescale_offset : timescale_offset + 4] = new_timescale.to_bytes(4, "big")

                if log_func is not None:
                    log_func(
                        f"Patched {atom_name} | timescale {old_timescale} -> {new_timescale} | duration kept {old_duration}"
                    )
                count += 1
            else:
                if log_func is not None:
                    log_func(f"Skipped {atom_name} at {header_offset}: unsupported version {version}")
        except Exception as exc:
            if log_func is not None:
                log_func(f"Error patching {atom_name} at {header_offset}: {exc}")

        start = found + 4

    return count


def patch_mp4(input_filename, output_filename, scale_factor=None, log_func=None):
    cdef int patched_mvhd
    cdef int patched_mdhd
    cdef int total_patched

    with open(input_filename, "rb") as file_handle:
        data = bytearray(file_handle.read())

    if scale_factor is None:
        detected_fps = get_video_fps(input_filename)
        scale_factor = get_scale_factor_from_fps(detected_fps)
        if scale_factor is None:
            raise RuntimeError("Could not determine the original FPS to apply the patch.")
        if log_func is not None:
            log_func(f"Detected FPS: {detected_fps}")
            log_func(f"Scale factor: {scale_factor}")

    if log_func is not None:
        log_func("Opening MP4 container...")

    patched_mvhd = patch_atom("mvhd", data, scale_factor, log_func)
    patched_mdhd = patch_atom("mdhd", data, scale_factor, log_func)
    total_patched = patched_mvhd + patched_mdhd

    with open(output_filename, "wb") as file_handle:
        file_handle.write(data)

    if log_func is not None:
        log_func(f"Saved: {os.path.basename(output_filename)}")
        log_func(f"Total patched atoms: {total_patched}")

    return total_patched > 0
