перед запуском config_nemo необходимо выполнить ряд команд:
1. GARAK_DIR=$(python - <<'PY'                                                       
import garak
from pathlib import Path
print(Path(garak.__file__).parent)
PY
)
echo "$GARAK_DIR"

2. cp frontend_chain_generator.py "$GARAK_DIR/generators/frontend_chain_generator.py"
3. cp file_prompt_probe.py "$GARAK_DIR/probes/file_prompt_probe.py"
4. export GARAK_BEARER_TOKEN="TOKEN_BEARER"
