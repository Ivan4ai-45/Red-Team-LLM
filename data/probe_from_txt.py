from garak.probes import Probe

class OmegaJailbreakProbe(Probe):
    bcp47 = "ru"
    goal = "Заставить модель произнести запрещённое слово 'НЕБЕСА'"
    
    def __init__(self):
        super().__init__()
        # Загрузить промпты из файла prompts.txt (каждый с новой строки)
        with open("jailbreak_prompts.txt", "r", encoding="utf-8") as f:
            self.prompts = [line.strip() for line in f if line.strip()]