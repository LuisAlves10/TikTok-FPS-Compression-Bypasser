"""Application translations and locale helpers."""

from __future__ import annotations

import locale


TRANSLATIONS = {
    "en": {
        "title": "Lenoz7 MP4 Patcher",
        "input_output": "Input and Output",
        "input_label": "Input video",
        "input_placeholder": "Select an MP4, MOV, or M4V file.",
        "output_label": "Save as",
        "output_placeholder": "Choose where the patched file will be saved.",
        "fps_label": "Original FPS",
        "fps_placeholder": "Optional. Leave blank for automatic detection.",
        "browse": "Browse",
        "auto": "Detect FPS",
        "clear": "Clear",
        "apply": "Apply patch",
        "console": "Processing console",
        "console_sub": "Follow the progress and patch details in real time.",
        "output": "Output",
        "ready": "Ready",
        "processing": "Processing",
        "done": "Done",
        "file_loaded": "File loaded",
        "cleared": "All fields have been cleared.",
        "start": "Starting patch...",
        "missing_input": "Select an input video.",
        "missing_output": "Choose where to save the patched file.",
        "invalid_input": "The input file does not exist.",
        "invalid_fps": "Enter a valid FPS value greater than zero.",
        "detected": "Detected FPS",
        "detect_failed": "Could not detect the FPS automatically.",
        "missing_detected_fps": "Could not determine the original FPS to apply the patch.",
        "nothing_patched": "No compatible atoms were found.",
        "success": "Patch completed successfully.",
        "open_folder": "Do you want to open the output folder?",
        "repo": "Original repository",
        "drag_hint": "Drop a video here or click to browse.",
        "drag_hint_no_dnd": "Click to browse. Install tkinterdnd2 to enable drag and drop.",
        "mode_manual": "Mode: manual FPS",
        "mode_auto": "Mode: automatic detection",
        "log_cleared": "Logs cleared.",
        "live_stats": "Live stats",
        "no_file_loaded": "No file loaded.",
        "tip": "Tip: use the top card to choose a video or the Browse buttons.",
        "ffprobe_unavailable": "unavailable (check ffprobe)",
        "output_path_set": "Output path set",
        "drop_failed": "Drop failed",
        "no_input_title": "No video",
        "detection_failed_title": "Detection failed",
        "invalid_fps_title": "Invalid FPS",
        "patch_failed_title": "Patch failed",
        "finished_title": "Finished",
        "nothing_patched_title": "No changes",
        "missing_input_title": "Input missing",
        "missing_output_title": "Output missing",
        "invalid_input_title": "Invalid file",
        "fps_detection_failed_title": "FPS detection failed",
    },
    "pt": {
        "title": "Lenoz7 MP4 Patcher",
        "input_output": "Entrada e saída",
        "input_label": "Vídeo de entrada",
        "input_placeholder": "Selecione um arquivo MP4, MOV ou M4V.",
        "output_label": "Salvar como",
        "output_placeholder": "Escolha onde o arquivo corrigido será salvo.",
        "fps_label": "FPS original",
        "fps_placeholder": "Opcional. Deixe em branco para detecção automática.",
        "browse": "Procurar",
        "auto": "Detectar FPS",
        "clear": "Limpar",
        "apply": "Aplicar patch",
        "console": "Console de processamento",
        "console_sub": "Acompanhe o progresso e os detalhes do patch em tempo real.",
        "output": "Saída",
        "ready": "Pronto",
        "processing": "Processando",
        "done": "Concluído",
        "file_loaded": "Arquivo carregado",
        "cleared": "Todos os campos foram limpos.",
        "start": "Iniciando patch...",
        "missing_input": "Selecione um vídeo de entrada.",
        "missing_output": "Escolha onde salvar o arquivo corrigido.",
        "invalid_input": "O arquivo de entrada não existe.",
        "invalid_fps": "Digite um valor de FPS válido e maior que zero.",
        "detected": "FPS detectado",
        "detect_failed": "Não foi possível detectar o FPS automaticamente.",
        "missing_detected_fps": "Não foi possível determinar o FPS original para aplicar o patch.",
        "nothing_patched": "Nenhum átomo compatível foi encontrado.",
        "success": "Patch concluído com sucesso.",
        "open_folder": "Deseja abrir a pasta de saída?",
        "repo": "Repositório original",
        "drag_hint": "Arraste um vídeo até aqui ou clique para procurar.",
        "drag_hint_no_dnd": "Clique para procurar. Instale o pacote tkinterdnd2 para habilitar o recurso de arrastar e soltar.",
        "mode_manual": "Modo: FPS manual",
        "mode_auto": "Modo: detecção automática",
        "log_cleared": "Logs limpos.",
        "live_stats": "Estatísticas",
        "no_file_loaded": "Nenhum arquivo carregado.",
        "tip": "Dica: use o cartão superior para escolher um vídeo ou os botões Procurar.",
        "ffprobe_unavailable": "indisponível (verifique o ffprobe)",
        "output_path_set": "Caminho de saída definido",
        "drop_failed": "Falha ao soltar o arquivo",
        "no_input_title": "Sem vídeo",
        "detection_failed_title": "Falha na detecção",
        "invalid_fps_title": "FPS inválido",
        "patch_failed_title": "Falha no patch",
        "finished_title": "Concluído",
        "nothing_patched_title": "Nenhuma alteração",
        "missing_input_title": "Vídeo ausente",
        "missing_output_title": "Saída ausente",
        "invalid_input_title": "Arquivo inválido",
        "fps_detection_failed_title": "Falha na leitura do FPS",
    },
}


def detect_language() -> str:
    candidates = []

    try:
        candidates.append(locale.getlocale()[0])
    except Exception:
        pass

    try:
        locale.setlocale(locale.LC_ALL, "")
        candidates.append(locale.getlocale()[0])
    except Exception:
        pass

    for value in candidates:
        if not value:
            continue
        normalized = value.lower()
        if normalized.startswith("pt"):
            return "pt"
        if normalized.startswith("en"):
            return "en"

    return "en"
