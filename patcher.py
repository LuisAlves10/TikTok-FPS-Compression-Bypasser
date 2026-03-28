#!/usr/bin/env python3
import subprocess
import sys


def get_video_fps(video_path):
    """
    Detecta o FPS original do vídeo usando ffprobe.
    Retorna um float ou None se não for possível detectar.
    """

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
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        if "/" in output:
            numerator, denominator = map(int, output.split("/"))
            return round(numerator / denominator, 2) if denominator else None
        return float(output)
    except Exception:
        return None


def get_scale_factor_from_fps(fps):
    """
    Calcula o fator usado para reduzir o timescale para o equivalente a 30 FPS.
    """

    if fps is None or fps <= 0:
        return None
    return 30 / fps


def patch_atom(atom_name, data, scale_factor=None):
    """
    Modifica os átomos "mvhd" ou "mdhd" dentro do arquivo MP4 para ajustar
    o timescale. A duração é mantida para preservar o comportamento esperado
    do método de bypass.

    Parâmetros:
    - atom_name: nome do átomo a ser modificado ("mvhd" ou "mdhd")
    - data: conteúdo binário do arquivo MP4 em um bytearray
    - scale_factor: fator manual para ajustar o timescale

    Retorna:
    - count: número de átomos modificados
    """

    count = 0
    start = 0
    atom_bytes = atom_name.encode("utf-8")

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

            print(
                f"Patched {atom_name} at offset {header_offset}: "
                f"timescale {old_timescale}->{new_timescale}, duração mantida {old_duration}"
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

            print(
                f"Patched {atom_name} at offset {header_offset}: "
                f"timescale {old_timescale}->{new_timescale}, duração mantida {old_duration}"
            )
            count += 1
        else:
            print(
                f"Found {atom_name} at offset {header_offset} "
                f"with unknown version {version}; skipping."
            )

        start = found + 4

    return count


def patch_mp4(input_filename, output_filename, scale_factor=None):
    """
    Abre um arquivo MP4, modifica os átomos "mvhd" e "mdhd" para ajustar o
    timescale e salva o arquivo modificado.

    Se nenhum fator for fornecido, o script tenta detectar o FPS original e
    calcular automaticamente o fator equivalente a 30 / FPS.
    """

    with open(input_filename, "rb") as file_handle:
        data = bytearray(file_handle.read())

    if scale_factor is None:
        detected_fps = get_video_fps(input_filename)
        scale_factor = get_scale_factor_from_fps(detected_fps)
        if scale_factor is None:
            raise RuntimeError("Não foi possível detectar o FPS original do vídeo.")

        print(f"Detected FPS: {detected_fps}")
        print(f"Using scale factor: {scale_factor}")

    patched_mvhd = patch_atom("mvhd", data, scale_factor)
    patched_mdhd = patch_atom("mdhd", data, scale_factor)

    total_patched = patched_mvhd + patched_mdhd
    print(f"\nTotal patched atoms: {total_patched}")

    with open(output_filename, "wb") as file_handle:
        file_handle.write(data)

    print(f"Patched file written to: {output_filename}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: patch_mp4.py input.mp4 output.mp4 [scale_factor (optional)]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    factor = None

    if len(sys.argv) > 3:
        try:
            factor = float(sys.argv[3])
        except ValueError:
            print("Invalid scale factor provided. Using automatic adjustment.")

    patch_mp4(input_file, output_file, scale_factor=factor)
