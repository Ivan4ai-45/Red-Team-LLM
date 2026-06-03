#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

DEFAULT_COL_CANDIDATES = [
    "prompt",
    "attack_prompt",
    "attackPrompt",
    "modified_prompt",
    "modifiedPrompt",
]

def newest_csv(hivetrace_out: Path) -> Path:
    csvs = sorted(
        hivetrace_out.glob("run_*/attack_prompts_*_results_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not csvs:
        raise FileNotFoundError(f"No attack_prompts_*_results_*.csv found under {hivetrace_out}")
    return csvs[0]

def detect_prompt_column(fieldnames, preferred=None):
    if preferred and preferred in fieldnames:
        return preferred
    for c in DEFAULT_COL_CANDIDATES:
        if c in fieldnames:
            return c
    return None

def export_txt(src_csv: Path, dst_txt: Path, prompt_col: str | None = None, dedupe: bool = True):
    with src_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        col = detect_prompt_column(cols, preferred=prompt_col)
        if not col:
            raise RuntimeError(
                f"Can't find prompt column. Available columns: {cols}\n"
                f"Pass --col <name> to choose explicitly."
            )

        seen = set()
        out = []
        for row in reader:
            s = (row.get(col) or "").replace("\n", " ").strip()
            if not s:
                continue
            if dedupe:
                if s in seen:
                    continue
                seen.add(s)
            out.append(s)

    dst_txt.parent.mkdir(parents=True, exist_ok=True)
    dst_txt.write_text("\n".join(out) + "\n", encoding="utf-8")
    return col, len(out)

def main():
    ap = argparse.ArgumentParser(description="Export HiveTraceRed Stage1 CSV prompts to a flat .txt list")
    ap.add_argument("--root", default=str(Path.home() / "llm-red"), help="Project root (default: ~/llm-red)")
    ap.add_argument("--hivetrace-out", default=None, help="Override hivetrace_out path")
    ap.add_argument("--prompt-dir", default=None, help="Override prompt/ dir path")
    ap.add_argument("--csv", default=None, help="Export this CSV instead of auto-detecting newest")
    ap.add_argument("--col", default=None, help="Column name to export (if auto-detect fails)")
    ap.add_argument("--no-dedupe", action="store_true", help="Do not deduplicate lines")
    ap.add_argument("--out-name", default=None, help="Override output filename (default: <csv-stem>.txt)")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    hivetrace_out = Path(args.hivetrace_out).expanduser().resolve() if args.hivetrace_out else (root / "hivetrace" / "hivetrace_out")
    prompt_dir = Path(args.prompt_dir).expanduser().resolve() if args.prompt_dir else (root / "prompt")

    src = Path(args.csv).expanduser().resolve() if args.csv else newest_csv(hivetrace_out)
    out_name = args.out_name if args.out_name else (src.stem + ".txt")
    dst = prompt_dir / out_name

    col, n = export_txt(src, dst, prompt_col=args.col, dedupe=not args.no_dedupe)
    print(f"[OK] {n} prompts exported from {src.name} (column={col}) -> {dst}")

if __name__ == "__main__":
    main()