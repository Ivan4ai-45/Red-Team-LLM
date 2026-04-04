#!/usr/bin/env python3
# run_garak_api.py

import sys
import json
from pathlib import Path
from datetime import datetime

def get_repo_root(start_path=None):
    if start_path is None:
        start_path = Path(__file__).parent
    for parent in [start_path] + list(start_path.parents):
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("Не удалось найти корень репозитория: нет папки .git")

REPO_ROOT = get_repo_root()
RESULTS_BASE = REPO_ROOT / "results" / "garak"
CUSTOM_PROMPTS_FILE = REPO_ROOT / "data" / "jailbreak_prompts.txt"  # Ваш файл с промптами

def run_garak_cli(config: dict, results_dir: Path):
    """Запускает Garak, программно создавая временный конфиг."""
    config_file = results_dir / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    import subprocess
    cmd = ["python", "-m", "garak", "--config", str(config_file)]
    print(f"🚀 Запуск: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def main():
    # Создаем папку для результатов
    run_dir = RESULTS_BASE / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    # Определяем, откуда брать промпты
    if CUSTOM_PROMPTS_FILE.exists():
        print(f"📂 Используем кастомные промпты из: {CUSTOM_PROMPTS_FILE}")
        probe_spec = ["file.File"]
        probe_options = {"file": {"source": f"file://{CUSTOM_PROMPTS_FILE}"}}
    else:
        print("⚠️ Файл с кастомными промптами не найден. Используем стандартные пробы.")
        probe_spec = ["dan.Dan_11_0", "lmrc.MaliciousCompliance", "jailbreak.JailbreakConversations"]
        probe_options = None

    # Формируем конфиг для Garak
    config = {
        "system": {
            "verbose": 2,
            "parallel_requests": 8,
            "parallel_attempts": 4,
        },
        "run": {
            "seed": 42,
            "generations": 5,
            "eval_threshold": 0.5,
            "deprefix": True,
        },
        "plugins": {
            "generators": {
                "ollama": {
                    "OllamaGenerator": {
                        "host": "http://localhost:11434",
                        "timeout": 120,
                    }
                }
            },
            "target_type": "ollama.OllamaGenerator",
            "target_name": "redteam-omega",
            "probe_spec": probe_spec,
            "detector_spec": "auto",
        },
        "reporting": {
            "report_prefix": "garak_scan_",
            "report_dir": str(run_dir),
        },
    }

    # Если используем кастомные промпты, добавляем опции для пробы
    if probe_options:
        config["plugins"]["probe_options"] = probe_options

    # Запускаем сканирование
    run_garak_cli(config, run_dir)

    print(f"\n✅ Сканирование завершено. Результаты в папке: {run_dir}")
    print(f"👉 Отчет: {run_dir}/garak_scan_.report.html")

if __name__ == "__main__":
    import yaml
    main()