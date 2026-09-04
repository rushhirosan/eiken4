#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate docs/inventory/level{4,5}/*.md from official archive question txts."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "docs" / "inventory"


def esc(s: str) -> str:
    return s.replace("|", "\\|")


def clip(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def q_focus(q: str) -> str:
    q = q.strip()
    rules = [
        (r"Who\b", "who（人物）"),
        (r"Where\b", "where（場所）"),
        (r"When\b", "when（時）"),
        (r"Why\b", "why（理由）"),
        (r"Which\b", "which（選択）"),
        (r"How many\b", "how many（数）"),
        (r"How much\b", "how much（金額・量）"),
        (r"How long\b", "how long（期間・長さ）"),
        (r"How old\b", "how old（年齢）"),
        (r"How often\b", "how often（頻度）"),
        (r"How far\b", "how far（距離）"),
        (r"How will\b|How (do|does|did|can)\b", "how（方法）"),
        (r"What kind\b", "what kind（種類）"),
        (r"What color\b", "what color（色）"),
        (r"What (is|are) .+ problem", "what（問題・困りごと）"),
        (r"What\b", "what（内容・行為）"),
        (r"Whose\b", "whose（所有）"),
    ]
    for pat, lab in rules:
        if re.match(pat, q, re.I):
            return lab
    return "その他"


def data_dir(level: str) -> Path:
    if level == "4":
        return ROOT / "data" / "questions"
    return ROOT / "data" / "questions" / f"level{level}"


def parse_numbered_blocks(path: Path) -> list[dict]:
    """問題N: ... 【正解】 【解説】 blocks."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    items = []
    for block in re.split(r"\n---\n+", text.strip()):
        m_q = re.search(r"問題(\d+):\s*(.*?)(?=\n選択肢\d+:|\n【正解|\n【参考解答】)", block, re.S)
        m_ans = re.search(r"【正解\d+】\s*\n?\s*\d+\.\s*([^\n]+)", block)
        m_exp = re.search(r"【解説\d+】\s*(.*)\Z", block, re.S)
        m_ref = re.search(r"【参考解答】\s*(.*)\Z", block, re.S)
        if not m_q:
            continue
        exp = ""
        if m_exp:
            exp = re.sub(r"\s+", " ", m_exp.group(1).strip())
        elif m_ref:
            exp = re.sub(r"\s+", " ", m_ref.group(1).strip())
        items.append(
            {
                "n": int(m_q.group(1)),
                "stem": re.sub(r"\s+", " ", m_q.group(2).strip()),
                "ans": m_ans.group(1).strip() if m_ans else "",
                "exp": exp,
            }
        )
    return items


def parse_listening(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    items = []
    for block in re.split(r"\n---\n+", text.strip()):
        m_no = re.search(r"No\.(\d+):", block)
        if not m_no:
            continue
        n = int(m_no.group(1))
        # broadcast lines before Question
        pre = block.split("Question No.")[0]
        broadcast = re.sub(r"\s+", " ", pre.split("\n", 1)[-1]).strip()[:120]
        qtext = ""
        mq = re.search(r"Question No\.\d+:\s*\n(.*?)(?=\n\d+\.\s|\n【正解)", block, re.S)
        if mq:
            first = mq.group(1).strip().split("\n")[0].strip()
            if not re.match(r"^\d+\.", first):
                qtext = first
        m_ans = re.search(r"【正解\d+】\s*\n?\s*\d+\.\s*([^\n]+)", block)
        m_exp = re.search(r"【解説\d+】\s*(.*)\Z", block, re.S)
        exp = re.sub(r"\s+", " ", m_exp.group(1).strip()) if m_exp else ""
        items.append(
            {
                "n": n,
                "question": qtext,
                "answer": m_ans.group(1).strip() if m_ans else "",
                "broadcast": broadcast,
                "exp": exp,
            }
        )
    return items


# ----- Grammar tagging -----

GRAMMAR_HINTS = [
    (r"現在完了", "現在完了"),
    (r"受動態|be動詞\s*＋\s*過去分詞|be動詞 \+ 過去分詞", "受動態"),
    (r"過去進行", "過去進行形"),
    (r"現在進行|be動詞＋動詞-ing|is \+ 動詞-ing|was \+ 動詞-ing", "進行形"),
    (r"関係代名詞|関係副詞|先行詞", "関係詞"),
    (r"比較級|最上級|more ～ than|than（", "比較"),
    (r"不定詞|to ＋ 動詞|to \+ 動詞|to do|to 不定詞", "不定詞"),
    (r"動名詞|-ing 形|～ing", "動名詞"),
    (r"付加疑問", "付加疑問"),
    (r"used to", "used to"),
    (r"have to|must（|助動詞", "助動詞・義務"),
    (r"too ～ to|enough to|a little|接続詞|although|because|if ", "文構造"),
    (r"三人称単数|過去形|時制", "時制・一致"),
]


PREPS = {
    "in", "on", "at", "for", "with", "to", "from", "of", "by", "about",
    "into", "over", "under", "between", "beside", "during", "without",
    "through", "after", "before", "around", "near", "up", "down", "off",
}
PRONOUNS = {
    "mine", "yours", "his", "hers", "ours", "theirs", "my", "your", "our",
    "their", "its", "who", "whose", "which", "what", "that", "this", "these",
    "those", "another", "other", "all", "both", "each", "some", "any",
    "little", "few", "much", "many", "enough", "he", "she", "they", "we", "it",
}
CONJS = {"and", "but", "or", "so", "because", "when", "if", "although", "while", "until", "since"}
MODALS = {"can", "could", "will", "would", "may", "might", "must", "should"}


def classify_grammar(item: dict) -> tuple[str, str, str]:
    """Return (kind, target, note)."""
    ans, exp = item["ans"], item["exp"]
    al = ans.lower().strip().rstrip(".,!")
    first = exp.split("。")[0] if exp else ""

    quotes = re.findall(r"「([^」]{1,60})」", exp)
    ticks = re.findall(r"`([^`]{1,60})`", exp)

    # function-word answers → 文法（級を問わず）
    if al in PREPS:
        return "文法", f"前置詞: {ans}", clip(first, 60)
    if al in PRONOUNS:
        return "文法", f"代名詞/限定詞: {ans}", clip(first, 60)
    if al in CONJS:
        return "文法", f"接続詞: {ans}", clip(first, 60)
    if al in MODALS:
        return "文法", f"助動詞: {ans}", clip(first, 60)
    if al.endswith("ing") and " " not in al and re.search(r"進行|-ing|いま|している", exp):
        return "文法", f"進行形: {ans}", clip(first, 60)
    if re.search(r"(er|est)$", al) or al.startswith("more ") or al in {
        "better", "best", "worse", "worst", "more", "most",
    }:
        if re.search(r"比較|than|より", exp) or al.startswith("more "):
            return "文法", f"比較: {ans}", clip(first, 60)

    phrase_cue = bool(
        re.search(
            r"熟語|決まった表現|決まり文句|定番表現|決まりの表現|定番の表現",
            exp,
        )
    )
    grammar_label = None
    for pat, lab in GRAMMAR_HINTS:
        if re.search(pat, exp):
            grammar_label = lab
            break

    pattern_q = None
    for q in quotes + ticks:
        if (
            re.search(
                r"～|〜|\bto\b|\bing\b|one'?s|A to B|not to|as .+ as|have |be ",
                q,
                re.I,
            )
            or " " in q
            or "～" in q
            or "〜" in q
        ):
            pattern_q = q
            break

    # Multi-word collocation in quotes → 熟語
    if phrase_cue or (
        pattern_q
        and (" " in pattern_q or "～" in pattern_q or "〜" in pattern_q)
        and re.search(r"look |be |get |take |come |go |have |good |front |way ", pattern_q, re.I)
    ):
        target = pattern_q or (quotes[0] if quotes else ans)
        return "熟語・定型", target, clip(first, 60)

    if grammar_label:
        target = pattern_q or (quotes[0] if quotes else ans)
        return "文法", f"{grammar_label}: {target}", clip(first, 60)

    # single-token 「X」で「…」意味説明 → 語彙
    gloss = ""
    m = re.search(r"「[^」]+」は「([^」]+)」", exp)
    if m:
        gloss = m.group(1)
    elif quotes:
        gloss = quotes[0]
    return "語彙", ans, gloss or clip(first, 60)


def classify_conversation(item: dict) -> tuple[str, str]:
    """Return (function, note)."""
    ans, exp = item["ans"], item["exp"]
    first = exp.split("。")[0] if exp else ""
    rules = [
        (r"謝[りる]|sorry|すみません", "謝罪"),
        (r"ありがとう|礼|You’re welcome|You are welcome", "礼・礼への返答"),
        (r"誘[いい]|提案|That sounds|I’d love|Good idea|一緒に", "誘い・提案への反応"),
        (r"断[りる]|できない|I can’t|No, thanks|No, thank", "断り"),
        (r"Because|理由", "理由の導入・説明"),
        (r"道案内|まっすぐ|turn left|Where .*銀行|場所を", "道案内・場所"),
        (r"現在完了|never|Have you|行ったこと", "経験（現在完了）"),
        (r"will|I’ll|つもり|これから", "意思・予定"),
        (r"依頼|Will you|Could you|お願い", "依頼"),
        (r"値段|How much|dollar", "値段・買い物"),
        (r"天気|雨|umbrella", "天気"),
        (r"感想|楽しかった|enjoy|great time", "感想"),
        (r"励まし|Good luck|大丈夫", "励まし"),
        (r"確認|Which .*talking|What time", "確認の疑問"),
        (r"快諾|Certainly|もちろん|Sure", "快諾"),
        (r"心配|worried|excited|happy", "感情表現"),
        (r"見送り|safe trip|Have a good", "見送り"),
    ]
    for pat, lab in rules:
        if re.search(pat, exp, re.I) or re.search(pat, ans, re.I):
            return lab, clip(first, 70)
    return "談話のつなぎ", clip(first, 70)


def classify_li_response(item: dict) -> tuple[str, str]:
    ans, exp, bc, q = item["answer"], item["exp"], item["broadcast"], item["question"]
    # If explicit Question line empty, use broadcast as the prompt
    prompt = q or bc
    focus = q_focus(prompt) if re.match(
        r"^(Who|Where|When|Why|Which|How|What|Whose)\b", prompt.strip(), re.I
    ) else ""

    rules = [
        (r"場所|Where |front of|over there|down the|behind", "場所の応答"),
        (r"時|When |o’clock|Tomorrow|On |At \d", "時の応答"),
        (r"理由|Why |Because", "理由の応答"),
        (r"提案|Let’s |Would you like", "提案・勧め"),
        (r"経験|I’ve |I have |been there", "経験"),
        (r"意思|I’ll |I will |I’m going to", "意思・予定"),
        (r"礼|pleasure|You’re welcome", "礼への返答"),
        (r"見送り|Have a (good|safe)|good time", "見送り"),
        (r"謝|sorry", "謝罪"),
        (r"断|I can’t|have to study|not a good idea", "断り・反対"),
        (r"励まし|hope you’re|I’m sure", "励ましへの反応"),
        (r"訂正|Actually", "誤解の訂正"),
        (r"受諾|I’d love|Sure|OK,", "受諾・応じ"),
    ]
    blob = ans + " " + exp
    for pat, lab in rules:
        if re.search(pat, blob, re.I):
            return lab, clip(ans + " ← " + (prompt[:50] or ""), 70)
    if focus:
        return f"疑問詞応答（{focus}）", clip(f"{prompt[:40]} → {ans}", 70)
    return "自然な応答", clip(exp.split("。")[0] if exp else ans, 70)


# ----- Writers -----

def write_header(level: str, title: str, src: str, form: str, stats: list[str]) -> list[str]:
    lines = [
        f"# {level}級公式保管：{title}で実際に聞かれていること",
        "",
        f"出所: `{src}`（保管用・公開登録しない）",
        "",
        f"形式: {form}",
        "",
    ]
    lines += [f"- {s}" for s in stats]
    lines += ["", "---", ""]
    return lines


def write_grammar(level: str, path: Path, out: Path) -> None:
    items = parse_numbered_blocks(path)
    rows = []
    by_kind: dict[str, list] = defaultdict(list)
    for it in items:
        kind, target, note = classify_grammar(it)
        row = {**it, "kind": kind, "target": target, "note": note}
        rows.append(row)
        by_kind[kind].append(row)

    src = str(path.relative_to(ROOT))
    lines = write_header(
        level,
        "文法・語彙",
        src,
        "短文／短い会話の空所補充（4択）",
        [
            f"総問数: **{len(items)}**",
            f"文法: **{len(by_kind['文法'])}**問",
            f"熟語・定型: **{len(by_kind['熟語・定型'])}**問",
            f"語彙: **{len(by_kind['語彙'])}**問",
            "※種別は解説文からの自動分類（目安）。境界例は解説を優先して確認すること。",
        ],
    )

    lines += ["## 1. 文法項目一覧", "", "| 項目 | 出題 No |", "|------|---------|"]
    gmap: dict[str, list[int]] = defaultdict(list)
    for r in by_kind["文法"]:
        gmap[r["target"]].append(r["n"])
    for t in sorted(gmap, key=lambda x: gmap[x][0]):
        nos = ", ".join(f"Q{n}" for n in gmap[t])
        lines.append(f"| {esc(t)} | {nos} |")

    lines += ["", "## 2. 熟語・定型一覧", "", "| 表現 | 補足 | 出題 No |", "|------|------|---------|"]
    pmap: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for r in by_kind["熟語・定型"]:
        pmap[r["target"]].append((r["n"], r["note"]))
    for t in sorted(pmap, key=lambda x: pmap[x][0][0]):
        nos = ", ".join(f"Q{n}" for n, _ in pmap[t])
        note = pmap[t][0][1]
        lines.append(f"| `{esc(t)}` | {esc(note)} | {nos} |")

    lines += ["", "## 3. 語彙一覧（正解語）", "", "| No | 正解 | 意味・ポイント |", "|----|------|----------------|"]
    for r in by_kind["語彙"]:
        lines.append(f"| Q{r['n']} | **{esc(r['ans'])}** | {esc(r['note'])} |")

    lines += [
        "",
        "---",
        "",
        "## 4. 全問台帳",
        "",
        "| No | 種別 | 聞いていること | 正解 | 補足 |",
        "|----|------|----------------|------|------|",
    ]
    for r in rows:
        lines.append(
            f"| Q{r['n']} | {r['kind']} | {esc(r['target'])} | `{esc(r['ans'])}` | {esc(r['note'])} |"
        )

    lines += [
        "",
        "## 5. オリジナル網羅チェック用メモ",
        "",
        "- 公開オリジナルの `【ポイント】見出し` と「聞いていること」列を突合する。",
        "- 語彙と熟語の境界は解説依存。コロケーションは熟語側に寄せている。",
        "",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_conversation(level: str, path: Path, out: Path) -> None:
    items = parse_numbered_blocks(path)
    rows = []
    by_fn: dict[str, list[int]] = defaultdict(list)
    for it in items:
        fn, note = classify_conversation(it)
        rows.append({**it, "fn": fn, "note": note})
        by_fn[fn].append(it["n"])

    src = str(path.relative_to(ROOT))
    lines = write_header(
        level,
        "会話補充",
        src,
        "会話の空所に入る応答・発話を選ぶ（4択）",
        [f"総問数: **{len(items)}**", "※談話機能は解説・正解からの自動分類（目安）。"],
    )
    lines += [
        "## 1. 談話機能の一覧",
        "",
        "| 談話機能 | 出題 No | 件数 |",
        "|----------|---------|------|",
    ]
    for fn in sorted(by_fn, key=lambda x: by_fn[x][0]):
        nos = ", ".join(f"Q{n}" for n in by_fn[fn])
        lines.append(f"| {fn} | {nos} | {len(by_fn[fn])} |")

    lines += [
        "",
        "---",
        "",
        "## 2. 全問台帳",
        "",
        "| No | 談話機能 | 正解 | 聞いていること | 場面要約 |",
        "|----|----------|------|----------------|----------|",
    ]
    for r in rows:
        lines.append(
            f"| Q{r['n']} | {r['fn']} | {esc(r['ans'])} | {esc(r['note'])} | {esc(clip(r['stem'], 90))} |"
        )
    lines += [
        "",
        "## 3. オリジナル網羅チェック用メモ",
        "",
        "- 誤答は別の疑問詞への答え・誘いと矛盾する文など、談話のつながりを壊すものが多い。",
        "- 機能（快諾／断り／理由／経験／意思）を先に決めてから作問すると偏りを防げる。",
        "",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_wordorder(level: str, path: Path, out: Path) -> None:
    items = parse_numbered_blocks(path)
    if not items:
        return
    # slots differ by level
    slot = "1番目と3番目" if level == "5" else "2番目と4番目"
    lines = write_header(
        level,
        "語順",
        str(path.relative_to(ROOT)),
        f"語句整序（日本文つき）。空所は **{slot}**。",
        [f"総問数: **{len(items)}**"],
    )
    lines += [
        "## 1. 全問台帳",
        "",
        "| No | 日本文（先頭） | 正解 | 解説の要点 |",
        "|----|----------------|------|------------|",
    ]
    for it in items:
        jp = it["stem"].split("①")[0].strip()
        tip = clip(it["exp"].split("。")[0] if it["exp"] else "", 70)
        lines.append(f"| Q{it['n']} | {esc(clip(jp, 40))} | `{esc(it['ans'])}` | {esc(tip)} |")

    # pattern hints from explanations
    lines += ["", "## 2. 解説に現れる語順パターン（抽出）", ""]
    pats = Counter()
    for it in items:
        for q in re.findall(r"「([^」]{4,50})」", it["exp"]):
            if "語順" in q or "+" in q or "＋" in q or "as " in q:
                pats[q] += 1
        for q in re.findall(r"(主語 \+ [^。]{5,40}|as \+ [^。]{5,40}|were \+ [^。]{5,40})", it["exp"]):
            pats[q] += 1
    if pats:
        lines += ["| パターン | 件数 |", "|----------|------|"]
        for p, c in pats.most_common(25):
            lines.append(f"| {esc(p)} | {c} |")
    else:
        lines.append("（解説から明示パターンを十分抽出できなかった。台帳の要点列を参照）")

    lines += [
        "",
        "## 3. オリジナル網羅チェック用メモ",
        "",
        f"- 空所位置（{slot}）と語数枠を崩さない。",
        "- 日本文が示す文型（進行・比較・疑問・不定詞など）のバランスを見る。",
        "",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_listening_illustration(level: str, path: Path, out: Path) -> None:
    items = parse_listening(path)
    if not items:
        return
    rows = []
    by_fn: dict[str, list[int]] = defaultdict(list)
    for it in items:
        fn, note = classify_li_response(it)
        rows.append({**it, "fn": fn, "note": note})
        by_fn[fn].append(it["n"])

    form = (
        "短い発話／会話への**自然な応答**（3択）。5級は第1部会話応答＋第3部イラスト一致を同一ファイルに含む場合あり。"
        if level == "5"
        else "短い会話の最後の発話への自然な応答（3択）。イラスト付き想定。"
    )
    lines = write_header(
        level,
        "リスニング第1部（イラスト・会話応答）",
        str(path.relative_to(ROOT)),
        form,
        [f"総問数: **{len(items)}**", "※談話機能は正解・解説からの自動分類（目安）。"],
    )
    lines += [
        "## 1. 応答の談話機能一覧",
        "",
        "| 談話機能 | 出題 No | 件数 |",
        "|----------|---------|------|",
    ]
    for fn in sorted(by_fn, key=lambda x: by_fn[x][0]):
        nos = ", ".join(f"No.{n}" for n in by_fn[fn])
        lines.append(f"| {fn} | {nos} | {len(by_fn[fn])} |")

    lines += [
        "",
        "---",
        "",
        "## 2. 全問台帳",
        "",
        "| No | 談話機能 | 正解 | 聞いていること |",
        "|----|----------|------|----------------|",
    ]
    for r in rows:
        lines.append(
            f"| No.{r['n']} | {r['fn']} | {esc(r['answer'])} | {esc(r['note'])} |"
        )
    lines += [
        "",
        "## 3. オリジナル網羅チェック用メモ",
        "",
        "- 正解は直前の疑問・発話への自然な続き。別の疑問詞への答えが典型ひっかけ。",
        "- 5級 No.101+ はイラスト一致パートの可能性あり（ファイル内番号を確認）。",
        "",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_listening_content(
    level: str, path: Path, out: Path, title: str, form: str, tips: list[str]
) -> None:
    items = parse_listening(path)
    if not items:
        return
    for it in items:
        it["focus"] = q_focus(it["question"]) if it["question"] else "その他"
    fc = Counter(it["focus"] for it in items)
    lines = write_header(
        level, title, str(path.relative_to(ROOT)), form, [f"総問数: **{len(items)}**"]
    )
    lines += [
        "## 1. 質問の聞き方（疑問詞・焦点）",
        "",
        "| 焦点 | 件数 | 出題 No |",
        "|------|------|---------|",
    ]
    for focus, _ in fc.most_common():
        nos = [it["n"] for it in items if it["focus"] == focus]
        lines.append(
            f"| {focus} | {len(nos)} | " + ", ".join(f"No.{n}" for n in nos) + " |"
        )
    lines += [
        "",
        "---",
        "",
        "## 2. 全問台帳",
        "",
        "| No | 焦点 | 質問 | 正解 |",
        "|----|------|------|------|",
    ]
    for it in items:
        lines.append(
            f"| No.{it['n']} | {it['focus']} | {esc(it['question'])} | {esc(it['answer'])} |"
        )
    lines += ["", "## 3. オリジナル網羅チェック用メモ", ""]
    lines += [f"- {t}" for t in tips]
    lines.append("")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reading(level: str, path: Path, out: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"\n(?=本文\d+\n)", text.strip())
    reading = []
    for part in parts:
        if not part.strip():
            continue
        m_head = re.match(r"本文(\d+)\n(.*?)(?=\n問題\d)", part, re.S)
        if not m_head:
            continue
        pnum = int(m_head.group(1))
        body = m_head.group(2)
        title = body.strip().split("\n")[0].strip()
        if title.startswith("From:"):
            sub = re.search(r"Subject:\s*(.+)", body)
            title = f"メール: {sub.group(1).strip()}" if sub else f"メール{pnum}"
        qs = []
        for qm in re.finditer(
            r"問題(\d+)([a-z]):\s*(.*?)(?=\n選択肢|\n【正解)", part, re.S
        ):
            qid = qm.group(1) + qm.group(2)
            qtext = re.sub(r"\s+", " ", qm.group(3).strip())
            am = re.search(rf"【正解{re.escape(qid)}】\s*\n?\s*\d+\.\s*([^\n]+)", part)
            ans = am.group(1).strip() if am else ""
            focus = q_focus(qtext)
            if focus == "その他":
                if re.match(r"What\b", qtext):
                    focus = "what（内容・行為）"
                elif re.search(r"\bbecause\b", qtext, re.I):
                    focus = "why（理由）"
                else:
                    focus = "細部・言い換え"
            qs.append({"id": qid, "q": qtext, "ans": ans, "focus": focus})
        nq = len(qs)
        ptype = "掲示・案内" if nq == 2 else ("メール" if nq == 3 else "物語・説明文")
        reading.append({"passage": pnum, "title": title, "type": ptype, "questions": qs})

    fc = Counter(q["focus"] for r in reading for q in r["questions"])
    lines = write_header(
        level,
        "読解",
        str(path.relative_to(ROOT)),
        "掲示・メール・物語／説明文の内容一致（セット構成）",
        [
            f"本文数: **{len(reading)}** / 設問数: **{sum(len(r['questions']) for r in reading)}**",
            f"掲示・案内: {sum(1 for r in reading if r['type']=='掲示・案内')} / "
            f"メール: {sum(1 for r in reading if r['type']=='メール')} / "
            f"物語・説明文: {sum(1 for r in reading if r['type']=='物語・説明文')}",
        ],
    )
    lines += [
        "## 1. パッセージ型",
        "",
        "| 本文 | 型 | タイトル | 設問数 |",
        "|------|----|----------|--------|",
    ]
    for r in reading:
        lines.append(
            f"| 本文{r['passage']} | {r['type']} | {esc(r['title'])} | {len(r['questions'])} |"
        )
    lines += ["", "## 2. 設問の焦点", "", "| 焦点 | 件数 |", "|------|------|"]
    for k, v in fc.most_common():
        lines.append(f"| {k} | {v} |")
    lines += [
        "",
        "---",
        "",
        "## 3. 全問台帳",
        "",
        "| 本文 | 型 | 設問 | 焦点 | 質問 | 正解 |",
        "|------|----|------|------|------|------|",
    ]
    for r in reading:
        for q in r["questions"]:
            lines.append(
                f"| 本文{r['passage']} | {r['type']} | {q['id']} | {q['focus']} | "
                f"{esc(clip(q['q'], 70))} | {esc(clip(q['ans'], 50))} |"
            )
    lines += [
        "",
        "## 4. オリジナル網羅チェック用メモ",
        "",
        "- セット構成（掲示2・メール3・物語5）を崩さない。",
        "- 物語末尾の要旨問（What is this story about?）を忘れない。",
        "",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_speaking(level: str, path: Path, out: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    speaking = []
    for m in re.finditer(r"問題(\d+):\s*(.*?)(?=\n---|\Z)", text, re.S):
        n = int(m.group(1))
        body = m.group(2)
        title_m = re.search(r"【Title】\s*\n(.+)", body)
        # tagged questions (L3/L4) or plain numbered (L5)
        qs = re.findall(
            r"(\d+)\.\s*\[(passage|illustration|personal)\]\s*(.+)", body
        )
        if qs:
            questions = [
                {"i": int(a), "type": b, "q": c.strip()} for a, b, c in qs
            ]
        else:
            raw = re.findall(r"(\d+)\.\s*(.+)", body.split("【Questions】")[-1].split("【参考解答】")[0])
            questions = []
            for a, c in raw:
                c = c.strip()
                # heuristic for L5: first two content, last personal
                questions.append({"i": int(a), "type": "?", "q": c})
            if level == "5" and len(questions) >= 3:
                for i, q in enumerate(questions):
                    if i < len(questions) - 1:
                        q["type"] = "passage"
                    else:
                        q["type"] = "personal"
            elif level == "4" and len(questions) == 4:
                # fallback if tags missing
                types = ["passage", "passage", "illustration", "personal"]
                for q, t in zip(questions, types):
                    q["type"] = t
        speaking.append(
            {
                "n": n,
                "title": title_m.group(1).strip() if title_m else "",
                "questions": questions,
            }
        )

    def count_type(t: str) -> int:
        return sum(1 for s in speaking for q in s["questions"] if q["type"] == t)

    form = {
        "5": "内容2＋自分1（イラストなし）",
        "4": "内容2＋イラスト1＋自分1",
        "3": "内容1＋イラスト2＋自分2",
    }.get(level, "")

    lines = write_header(
        level,
        "スピーキング",
        str(path.relative_to(ROOT)),
        form,
        [f"カード数: **{len(speaking)}**"],
    )
    lines += [
        "## 1. 質問タイプの内訳",
        "",
        "| タイプ | 件数 |",
        "|--------|------|",
        f"| passage | {count_type('passage')} |",
        f"| illustration | {count_type('illustration')} |",
        f"| personal | {count_type('personal')} |",
        "",
        "## 2. トピック一覧",
        "",
        "| No | タイトル | 質問一覧 |",
        "|----|----------|----------|",
    ]
    for s in speaking:
        qs = " / ".join(f"[{q['type']}] {q['q']}" for q in s["questions"])
        lines.append(f"| Q{s['n']} | {esc(s['title'])} | {esc(qs)} |")

    lines += [
        "",
        "## 3. 全問台帳",
        "",
        "| カード | No | タイプ | 質問 |",
        "|--------|----|--------|------|",
    ]
    for s in speaking:
        for q in s["questions"]:
            lines.append(
                f"| Q{s['n']} {esc(s['title'])} | {q['i']} | {q['type']} | {esc(q['q'])} |"
            )
    lines += [
        "",
        "## 4. オリジナル網羅チェック用メモ",
        "",
        f"- 級の配分（{form}）を崩さない。",
        "- イラスト問は進行形、パーソナルは Do you / What do you like などが定番。",
        "",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_level(level: str) -> list[str]:
    d = data_dir(level)
    out_dir = INV / f"level{level}"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    mapping = [
        ("grammar_fill_questions.txt", "grammar_vocabulary.md", write_grammar),
        ("conversation_questions.txt", "conversation.md", write_conversation),
        ("wordorder_questions.txt", "wordorder.md", write_wordorder),
        ("speaking_questions.txt", "speaking.md", write_speaking),
        (
            "listening_illustration_questions.txt",
            "listening_illustration.md",
            write_listening_illustration,
        ),
        ("reading_comprehesion_questions.txt", "reading_comprehension.md", write_reading),
    ]
    for src_name, out_name, fn in mapping:
        src = d / src_name
        if not src.exists():
            continue
        fn(level, src, out_dir / out_name)
        written.append(out_name)

    # content listening
    lc = d / "listening_conversation_questions.txt"
    if lc.exists():
        write_listening_content(
            level,
            lc,
            out_dir / "listening_conversation.md",
            "リスニング第2部（会話内容一致）",
            "会話を聞き内容一致の選択肢を選ぶ。",
            [
                "会話に出たが答えではない情報がひっかけになりやすい。",
                "who/what/when/where/why/how のバランスを公開セットでも意識する。",
            ],
        )
        written.append("listening_conversation.md")

    lp = d / "listening_passage_questions.txt"
    if lp.exists():
        write_listening_content(
            level,
            lp,
            out_dir / "listening_passage.md",
            "リスニング第3部（文・モノローグ内容一致）",
            "短いモノローグを聞き内容一致の選択肢を選ぶ。",
            [
                "複数の数字・予定から質問が指す1点だけを取る。",
                "既知の事実とこれからやることを取り違えない。",
            ],
        )
        written.append("listening_passage.md")

    return written


def update_readme(level_files: dict[str, list[str]]) -> None:
    lines = [
        "# 公式保管問題の出題内容インベントリ",
        "",
        "`data/questions/`（級別 txt）で**実際に聞かれていること**を級・カテゴリごとに整理した台帳。",
        "オリジナル作問の網羅チェック用。公式文面の転載・公開登録用ではない。",
        "",
        "## 構成",
        "",
        "```",
        "docs/inventory/",
        "  level3/   # 手厚め分類（既存）",
        "  level4/",
        "  level5/",
        "```",
        "",
        "| 級 | 状態 | 備考 |",
        "|----|------|------|",
        "| 3級 | [`level3/`](level3/) | 公式保管カテゴリ一式（語順ファイルなし） |",
        "| 4級 | [`level4/`](level4/) | 語順・読解あり。ライティングなし |",
        "| 5級 | [`level5/`](level5/) | 語順あり。読解・ライティング・L文章なし |",
        "",
        "## ファイル一覧",
        "",
    ]
    for lv in ("3", "4", "5"):
        lines.append(f"### {lv}級")
        lines.append("")
        files = level_files.get(lv, [])
        if not files:
            # list existing dir
            p = INV / f"level{lv}"
            files = sorted(x.name for x in p.glob("*.md")) if p.exists() else []
        for f in files:
            lines.append(f"- [`level{lv}/{f}`](level{lv}/{f})")
        lines.append("")
    lines += [
        "## 再生成",
        "",
        "```bash",
        "python scripts/gen_official_inventory.py          # 4級・5級",
        "python scripts/gen_level3_inventory.py            # 3級の一部カテゴリ",
        "```",
        "",
        "4・5級の文法／会話／L応答の種別は解説ベースの自動分類（目安）。",
        "3級の文法・会話は手作業タグを含む既存台帳を優先。",
        "",
    ]
    (INV / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    results = {}
    for level in ("4", "5"):
        written = generate_level(level)
        results[level] = sorted(written)
        print(f"level{level}:", ", ".join(results[level]))
    # include level3 existing
    p3 = INV / "level3"
    results["3"] = sorted(x.name for x in p3.glob("*.md")) if p3.exists() else []
    update_readme(results)
    print("README updated")


if __name__ == "__main__":
    main()
