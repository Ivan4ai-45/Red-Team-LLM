#!/usr/bin/env python3
import argparse
import random
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def load_lines(path: Path):
    lines = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                lines.append(s)
    return lines

def save_lines(path: Path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for s in lines:
            f.write(s.replace("\n", " ").strip() + "\n")

def paraphrase(
    texts,
    model_name: str,
    n_variants: int,
    seed: int,
    max_input: int,
    max_new: int,
    num_beams: int,
    device: str,
):
    random.seed(seed)
    torch.manual_seed(seed)

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    out = []
    for t in texts:
        # ограничим длину входа
        enc = tok(
            t,
            return_tensors="pt",
            truncation=True,
            max_length=max_input,
        ).to(device)

        # генерим несколько вариантов
        gen = model.generate(
            **enc,
            do_sample=False,
            num_beams=num_beams,
            num_return_sequences=n_variants,
            max_new_tokens=max_new,
        )

        variants = tok.batch_decode(gen, skip_special_tokens=True)
        for v in variants:
            v = " ".join(v.strip().split())
            if v:
                out.append(v)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", required=True)
    ap.add_argument("--outfile", required=True)
    ap.add_argument("--model", required=True, help="HF model name used for paraphrasing")
    ap.add_argument("--n", type=int, default=3, help="paraphrases per input line")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max_input", type=int, default=256)
    ap.add_argument("--max_new", type=int, default=64)
    ap.add_argument("--beams", type=int, default=8)
    ap.add_argument("--include_original", action="store_true")
    ap.add_argument("--dedupe", action="store_true")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    args = ap.parse_args()

    infile = Path(args.infile)
    outfile = Path(args.outfile)

    src = load_lines(infile)
    paras = paraphrase(
        src,
        model_name=args.model,
        n_variants=args.n,
        seed=args.seed,
        max_input=args.max_input,
        max_new=args.max_new,
        num_beams=args.beams,
        device=args.device,
    )

    combined = []
    if args.include_original:
        combined.extend(src)
    combined.extend(paras)

    # дедуп + сохранение порядка
    if args.dedupe:
        seen = set()
        uniq = []
        for s in combined:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        combined = uniq

    save_lines(outfile, combined)
    print(f"Wrote {len(combined)} lines to {outfile}")

if __name__ == "__main__":
    main()