#!/usr/bin/env python3
"""
2025年度 英検3級 一次試験の過去問PDF・公式解答PDFの抽出テキストから、
data/questions/level3/ 向けの登録用テキストを生成する。

入力（既定パス）:
  data/pdf_import/level3_kakomon/2025-{1,2,3}_3kyu_extracted.txt
  data/pdf_import/level3_kakomon/202501_{502,503}_answers_extracted.txt

・リスニング・語順は対象外（語順はテキストを出力しない＝登録0でよい場合は空にする）。
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IMPORT_DIR = BASE_DIR / "data/pdf_import/level3_kakomon"
OUT_DIR = BASE_DIR / "data/questions/level3"

SESSIONS = (
    {
        "id": "2025-1",
        "booklet": "2025-1_3kyu_extracted.txt",
        "answers": "202501_answers_extracted.txt",
        "markers": ("Volunteer Work", "From: Bryan", "The Three Sisters"),
    },
    {
        "id": "2025-2",
        "booklet": "2025-2_3kyu_extracted.txt",
        "answers": "202502_answers_extracted.txt",
        "markers": ("Notice", "From: Sophia", "La Tomatina"),
    },
    {
        "id": "2025-3",
        "booklet": "2025-3_3kyu_extracted.txt",
        "answers": "202503_answers_extracted.txt",
        "markers": ("To All Students", "From: Lucas", "Ansel Adams"),
    },
)


def parse_answers(ans_text: str) -> dict[int, int]:
    out: dict[int, int] = {}
    lines = ans_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r"^\((\d+)\)$", line)
        if m:
            q = int(m.group(1))
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                al = lines[j].strip()
                if re.match(r"^[1-4]$", al):
                    out[q] = int(al)
            i = j + 1
            continue
        i += 1
    return out


def split_blocks(text: str) -> dict[int, str]:
    pat = re.compile(r"^\((\d+)\)\s*$", re.MULTILINE)
    matches = list(pat.finditer(text))
    blocks: dict[int, str] = {}
    for i, m in enumerate(matches):
        n = int(m.group(1))
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks[n] = text[start:end].strip()
    return blocks


def gap_between(text: str, after_q: int, before_q: int) -> str:
    pat = re.compile(r"^\((\d+)\)\s*$", re.MULTILINE)
    matches = {int(m.group(1)): m for m in pat.finditer(text)}
    return text[matches[after_q].end() : matches[before_q].start()]


def normalize_stem(line_list: list[str]) -> str:
    """PDF抽出では英文が1語ずつ改行されることがあるのでスペースで結合する。"""
    parts = [ln.strip() for ln in line_list if ln.strip()]
    s = " ".join(parts)
    s = re.sub(r"\(\s*\)", "( )", s)
    return s.strip()


def parse_mc_block(block: str) -> tuple[str, list[str]]:
    lines = block.split("\n")
    if lines and lines[0].startswith("("):
        lines = lines[1:]
    lines = [l.rstrip() for l in lines]
    clean_lines: list[str] = []
    for ln in lines:
        if "つぎ" in ln or "2025年度第" in ln or "copyright" in ln.lower():
            break
        clean_lines.append(ln)
    lines = clean_lines
    choice_start = None
    for i, ln in enumerate(lines):
        if re.match(r"^[1-4]$", ln.strip()):
            choice_start = i
            break
    if choice_start is None:
        raise ValueError("choices not found")
    stem_lines = lines[:choice_start]
    stem = normalize_stem(stem_lines)
    choices: list[str] = []
    i = choice_start
    while i < len(lines) and len(choices) < 4:
        num = lines[i].strip()
        if not re.match(r"^[1-4]$", num):
            break
        i += 1
        if i >= len(lines):
            break
        txt = lines[i].strip()
        i += 1
        choices.append(txt)
    if len(choices) != 4:
        raise ValueError(f"expected 4 choices, got {len(choices)}")
    return stem, choices


def normalize_passage_text(raw: str) -> str:
    lines = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        if "copyright" in line.lower():
            break
        if "2025年度第" in line and "検定" in line:
            break
        if line.startswith("Grade 3"):
            continue
        if re.fullmatch(
            r"[\u3040-\u30ff\u4e00-\u9fff\s\d\-−・，、。：（）●■▼☆♪＊]+",
            line,
        ):
            continue
        lines.append(line)
    text = " ".join(lines)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def passage_from_gap(gap: str, marker: str) -> str:
    idx = gap.find(marker)
    if idx == -1:
        raise ValueError(f"marker not found: {marker!r}")
    raw = gap[idx:]
    return normalize_passage_text(raw)


def letter_suffix(q_index: int) -> str:
    # 1 -> a, 2 -> b, ... 26 -> z
    return chr(ord("a") + q_index - 1)


def format_mc_question(
    display_num: int,
    stem: str,
    choices: list[str],
    correct_idx: int,
    explanation: str,
) -> str:
    """correct_idx: 1-4"""
    correct_text = choices[correct_idx - 1]
    lines = [
        f"問題{display_num}:",
        stem,
        "",
        f"選択肢{display_num}:",
    ]
    for i, c in enumerate(choices, 1):
        lines.append(f"{i}. {c}")
    lines.extend(
        [
            "",
            f"【正解{display_num}】",
            f"{correct_idx}. {correct_text}",
            "",
            f"【解説{display_num}】",
            explanation,
            "",
            "---",
            "",
        ]
    )
    return "\n".join(lines)


def format_reading_question(
    passage_num: int,
    q_index_in_passage: int,
    stem: str,
    choices: list[str],
    correct_idx: int,
    explanation: str,
) -> str:
    suf = letter_suffix(q_index_in_passage)
    tag = f"{passage_num}{suf}"
    correct_text = choices[correct_idx - 1]
    lines = [
        f"問題{tag}:",
        stem,
        "",
        f"選択肢{tag}:",
    ]
    for i, c in enumerate(choices, 1):
        lines.append(f"{i}. {c}")
    lines.extend(
        [
            "",
            f"【正解{tag}】",
            f"{correct_idx}. {correct_text}",
            "",
            f"【解説{tag}】",
            explanation,
            "",
        ]
    )
    return "\n".join(lines)


def run(out_dir: Path, dry_run: bool) -> None:
    grammar_parts: list[str] = []
    conversation_parts: list[str] = []
    reading_blocks: list[str] = []

    g_base = 0
    c_base = 0
    passage_base = 0

    expl_g = "公式一次試験の解答（協会発表の解答速報PDF）に基づく。"
    expl_r = "公式解答（協会発表の解答速報PDF）に基づく。"

    for session in SESSIONS:
        booklet_path = IMPORT_DIR / session["booklet"]
        answers_path = IMPORT_DIR / session["answers"]
        text = booklet_path.read_text(encoding="utf-8")
        answers = parse_answers(answers_path.read_text(encoding="utf-8"))
        blocks = split_blocks(text)
        m_a, m_b, m_c = session["markers"]

        # --- Grammar (1)-(15) ---
        for n in range(1, 16):
            stem, choices = parse_mc_block(blocks[n])
            g_num = g_base + n
            grammar_parts.append(
                format_mc_question(g_num, stem, choices, answers[n], expl_g)
            )

        # --- Conversation (16)-(20) ---
        for j, n in enumerate(range(16, 21), start=1):
            stem, choices = parse_mc_block(blocks[n])
            c_num = c_base + j
            conversation_parts.append(
                format_mc_question(c_num, stem, choices, answers[n], expl_g)
            )

        # --- Reading: 3 passages ---
        g20_21 = gap_between(text, 20, 21)
        g22_23 = gap_between(text, 22, 23)
        g25_26 = gap_between(text, 25, 26)
        passage_a = passage_from_gap(g20_21, m_a)
        passage_b = passage_from_gap(g22_23, m_b)
        passage_c = passage_from_gap(g25_26, m_c)

        p1 = passage_base + 1
        p2 = passage_base + 2
        p3 = passage_base + 3

        rb1 = [f"本文{p1}", passage_a, ""]
        rb2 = [f"本文{p2}", passage_b, ""]
        rb3 = [f"本文{p3}", passage_c, ""]

        # Passage p1: (21)(22)
        for q_in_p, n in enumerate((21, 22), start=1):
            stem, choices = parse_mc_block(blocks[n])
            rb1.append(
                format_reading_question(p1, q_in_p, stem, choices, answers[n], expl_r)
            )
        rb1.append("---")
        reading_blocks.append("\n".join(rb1))

        # Passage p2: (23)(24)(25)
        for q_in_p, n in enumerate((23, 24, 25), start=1):
            stem, choices = parse_mc_block(blocks[n])
            rb2.append(
                format_reading_question(p2, q_in_p, stem, choices, answers[n], expl_r)
            )
        rb2.append("---")
        reading_blocks.append("\n".join(rb2))

        # Passage p3: (26)-(30)
        for q_in_p, n in enumerate(range(26, 31), start=1):
            stem, choices = parse_mc_block(blocks[n])
            rb3.append(
                format_reading_question(p3, q_in_p, stem, choices, answers[n], expl_r)
            )
        rb3.append("---")
        reading_blocks.append("\n".join(rb3))

        g_base += 15
        c_base += 5
        passage_base += 3

    grammar_out = "\n".join(grammar_parts).rstrip() + "\n"
    conversation_out = "\n".join(conversation_parts).rstrip() + "\n"
    reading_out = "\n\n".join(reading_blocks).rstrip() + "\n"

    if dry_run:
        print(grammar_out[:1200])
        print("...", len(grammar_out), "bytes grammar")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "grammar_fill_questions.txt").write_text(grammar_out, encoding="utf-8")
    (out_dir / "conversation_questions.txt").write_text(
        conversation_out, encoding="utf-8"
    )
    (out_dir / "reading_comprehesion_questions.txt").write_text(
        reading_out, encoding="utf-8"
    )
    print(f"Wrote {out_dir / 'grammar_fill_questions.txt'}")
    print(f"Wrote {out_dir / 'conversation_questions.txt'}")
    print(f"Wrote {out_dir / 'reading_comprehesion_questions.txt'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=OUT_DIR,
        help="出力先（既定: data/questions/level3）",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="ファイルは書かず先頭のみ表示",
    )
    args = ap.parse_args()
    run(args.out_dir, args.dry_run)


if __name__ == "__main__":
    main()
