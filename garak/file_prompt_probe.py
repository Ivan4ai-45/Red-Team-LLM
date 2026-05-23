from pathlib import Path

import garak.probes
from garak import _config

class FilePromptProbe(garak.probes.Probe):
    """Probe, загружающий промпты из текстового файла построчно."""

    active = False
    bcp47 = "en"
    goal = "test system prompt extraction"
    primary_detector = "mitigation.MitigationBypass"

    DEFAULT_PARAMS = {
        "prompts_file": "../prompt/extract_system_prompt.txt",
    }

    def __init__(self, config_root=_config):
        super().__init__(config_root=config_root)

        self.prompts = []

        path = Path(self.prompts_file).expanduser()

        if not path.exists():
            raise FileNotFoundError(f"Prompts file not found: {path.resolve()}")

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.prompts.append(line)

        if not self.prompts:
            raise ValueError(f"No prompts loaded from {path.resolve()}")