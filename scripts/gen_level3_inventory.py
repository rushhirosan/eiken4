#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate docs/inventory/level3/*.md for remaining categories (not grammar/conversation)."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "inventory" / "level3"
DATA = ROOT / "data" / "questions" / "level3"


def q_focus(q: str) -> str:
    q = q.strip()
    if re.match(r"Who\b", q):
        return "who（人物）"
    if re.match(r"Where\b", q):
        return "where（場所）"
    if re.match(r"When\b", q):
        return "when（時）"
    if re.match(r"Why\b", q):
        return "why（理由）"
    if re.match(r"Which\b", q):
        return "which（選択）"
    if re.match(r"How many\b", q, re.I):
        return "how many（数）"
    if re.match(r"How much\b", q, re.I):
        return "how much（金額・量）"
    if re.match(r"How long\b", q, re.I):
        return "how long（期間・長さ）"
    if re.match(r"How old\b", q, re.I):
        return "how old（年齢）"
    if re.match(r"How often\b", q, re.I):
        return "how often（頻度）"
    if re.match(r"How will\b|How (do|does|did|can)\b", q, re.I):
        return "how（方法）"
    if re.match(r"What kind\b", q, re.I):
        return "what kind（種類）"
    if re.match(r"What (is|are) .+ problem", q, re.I):
        return "what（問題・困りごと）"
    if re.match(r"What\b", q):
        return "what（内容・行為）"
    return "その他"


def parse_listening(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    items = []
    for block in re.split(r"\n---\n+", text.strip()):
        m_no = re.search(r"No\.(\d+):", block)
        if not m_no:
            continue
        n = int(m_no.group(1))
        qtext = ""
        mq = re.search(
            r"Question No\.\d+:\s*\n(.*?)(?=\n\d+\.\s|\n【正解)",
            block,
            re.S,
        )
        if mq:
            first = mq.group(1).strip().split("\n")[0].strip()
            if not re.match(r"^\d+\.", first):
                qtext = first
        m_ans = re.search(r"【正解\d+】\s*\n?\s*\d+\.\s*([^\n]+)", block)
        answer = m_ans.group(1).strip() if m_ans else ""
        items.append({"n": n, "question": qtext, "answer": answer})
    return items


LI_FN = {
    1: ("場所の応答", "Where への答え（理科室の前）"),
    2: ("励ましへの反応", "I hope you’re right.（そうだといいな）"),
    3: ("提案", "Let’s find the elevator（階段を避けたい流れ）"),
    4: ("経験の共有", "I’ve been there, too.（現在完了）"),
    5: ("別れ・再訪の意思", "I’ll come back to visit soon."),
    6: ("人物情報の補足", "He’s a college student.（兄の説明）"),
    7: ("再会への反応", "I’m glad you remember me."),
    8: ("誤解の訂正", "Actually, I walked to school."),
    9: ("場所の案内", "It’s just down the street."),
    10: ("誘いの受諾", "I’d love to."),
    11: ("感想", "I enjoyed it a lot."),
    12: ("持ち物・ものの特定", "A garbage bag.（何を持っているか）"),
    13: ("予定・意思", "I’m going to buy one."),
    14: ("感想・評価", "The topic was interesting."),
    15: ("呼びかけへの応答", "OK, I’m coming.（電話に出る）"),
    16: ("状態の理由", "I drank some water.（暑そうへの返答）"),
    17: ("出来事の詳細", "He gave me a ring."),
    18: ("乗降・場所の詳細", "At the second stop."),
    19: ("状況説明", "They are sleeping."),
    20: ("人物の特徴", "She has many books."),
    21: ("励ましへの同意", "I’m sure they will."),
    22: ("礼への返答", "My pleasure."),
    23: ("要求への応じ", "OK, I’ll get my wallet."),
    24: ("所有の案内", "Yours is over there."),
    25: ("調べる申し出", "Sure, I’ll look on the Internet."),
    26: ("経験", "I’ve been there twice."),
    27: ("数量の応答", "Three large ones."),
    28: ("探し物の結果", "She didn’t see it there."),
    29: ("見送り", "Have a good time."),
    30: ("可能性への同意", "I think they can."),
    31: ("申し出・共有", "You can share mine."),
    32: ("探し方の提案", "Let’s look in your desk."),
    33: ("理由の説明", "The wind is very strong."),
    34: ("勧め", "Would you like to try one?"),
    35: ("代わりにしたこと", "I watched TV instead."),
    36: ("代替策", "I’ll buy something at the cafeteria."),
    37: ("提案・誘い", "Would you like to see them later?"),
    38: ("場所の案内", "It’s behind the main building."),
    39: ("年齢・属性", "He’s five years old."),
    40: ("称賛への反応", "I really am."),
    41: ("種類の説明", "It’s science fiction."),
    42: ("返却の約束", "I can bring it tomorrow."),
    43: ("断りの理由", "I have to study for a test."),
    44: ("店員・勧めへの反応", "I’m sure I will."),
    45: ("行き先", "To a beach in Thailand."),
    46: ("頻度・習慣", "For one hour every afternoon."),
    47: ("礼への返答", "It’s my pleasure."),
    48: ("探し物の結果", "She couldn’t find it there."),
    49: ("改善の意思", "Oh, I’ll get new ones."),
    50: ("反対・助言", "That’s not a good idea."),
}


def write_listening_illustration(items: list[dict]) -> None:
    by_fn: dict[str, list[int]] = defaultdict(list)
    for it in items:
        fn, _ = LI_FN[it["n"]]
        by_fn[fn].append(it["n"])

    lines = [
        "# 3級公式保管：リスニング第1部（イラスト・会話応答）で実際に聞かれていること",
        "",
        "出所: `data/questions/level3/listening_illustration_questions.txt`（保管用・公開登録しない）",
        "",
        "形式: 短い会話の**最後の発話への自然な応答**を選ぶ（3択）。画面上はイラスト付き想定。",
        "",
        f"- 総問数: **{len(items)}**",
        "",
        "---",
        "",
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
        "## 2. よく出るパターン",
        "",
        "| パターン | 内容 |",
        "|----------|------|",
        "| 場所・道案内 | It’s just down the street / behind the main building / At the second stop |",
        "| 経験（現在完了） | I’ve been there, too / twice |",
        "| will の意思・申し出 | I’ll get / buy / look / come back |",
        "| Let’s / Would you like | 提案・勧め |",
        "| 礼・見送り | My pleasure / Have a good time |",
        "| 探し物の結果 | She didn’t / couldn’t find it |",
        "| 励まし・称賛への反応 | I hope you’re right / I really am / I’m sure they will |",
        "",
        "---",
        "",
        "## 3. 全問台帳",
        "",
        "| No | 談話機能 | 正解 | 聞いていること |",
        "|----|----------|------|----------------|",
    ]
    for it in items:
        fn, note = LI_FN[it["n"]]
        ans = it["answer"].replace("|", "\\|")
        lines.append(f"| No.{it['n']} | {fn} | {ans} | {note} |")

    lines += [
        "",
        "## 4. オリジナル網羅チェック用メモ",
        "",
        "- 正解は**最後の発話への自然な続き**。別話題・矛盾・別の疑問詞への答えがひっかけ。",
        "- 3級らしさ: 現在完了の経験、will、提案（Let’s / Would you like）、場所表現、探し物。",
        "- オリジナルも「直前発話の機能 → 応答機能」を先に決めると偏りを防げる。",
        "",
    ]
    (OUT / "listening_illustration.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_listening_qa(
    path_name: str,
    title: str,
    form: str,
    items: list[dict],
    tips: list[str],
    info_rows: list[tuple[str, str]],
) -> None:
    for it in items:
        it["focus"] = q_focus(it["question"])
    fc = Counter(it["focus"] for it in items)

    lines = [
        f"# 3級公式保管：{title}で実際に聞かれていること",
        "",
        f"出所: `data/questions/level3/{path_name}`（保管用・公開登録しない）",
        "",
        f"形式: {form}",
        "",
        f"- 総問数: **{len(items)}**",
        "",
        "---",
        "",
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
        "## 2. よく取らせる情報",
        "",
        "| 情報の種類 | 例 |",
        "|------------|----|",
    ]
    for kind, example in info_rows:
        lines.append(f"| {kind} | {example} |")

    lines += [
        "",
        "---",
        "",
        "## 3. 全問台帳",
        "",
        "| No | 焦点 | 質問 | 正解 |",
        "|----|------|------|------|",
    ]
    for it in items:
        q = it["question"].replace("|", "\\|")
        a = it["answer"].replace("|", "\\|")
        lines.append(f"| No.{it['n']} | {it['focus']} | {q} | {a} |")

    lines += ["", "## 4. オリジナル網羅チェック用メモ", ""]
    lines += [f"- {t}" for t in tips]
    lines.append("")

    out_name = path_name.replace("_questions.txt", ".md")
    (OUT / out_name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_writing() -> None:
    text = (DATA / "writing_questions.txt").read_text(encoding="utf-8")
    writing = []
    for m in re.finditer(r"問題(\d+):\s*(.*?)(?=\n---|\Z)", text, re.S):
        n = int(m.group(1))
        body = m.group(2)
        kind = "Eメール" if "<u>" in body else "意見論述"
        uqs = re.findall(r"<u>(.*?)</u>", body)
        q = re.search(r"QUESTION\s*\n(.+)", body)
        topic = ""
        if kind == "Eメール":
            mm = re.search(
                r"Thank you for your e-mail\.\s*(.+?)(?:I have some questions|$)",
                body,
                re.S,
            )
            if mm:
                topic = re.sub(r"\s+", " ", mm.group(1).strip())[:80]
        writing.append(
            {
                "n": n,
                "kind": kind,
                "underlines": uqs,
                "question": q.group(1).strip() if q else "",
                "topic": topic,
            }
        )

    emails = [w for w in writing if w["kind"] == "Eメール"]
    opinions = [w for w in writing if w["kind"] == "意見論述"]
    wh_c: Counter[str] = Counter()
    for w in emails:
        for u in w["underlines"]:
            m = re.match(
                r"(And )?(What|Where|When|Which|Who|How many|How often|How did|Did)\b",
                u,
            )
            wh_c[m.group(2) if m else "Other"] += 1

    lines = [
        "# 3級公式保管：ライティングで実際に聞かれていること",
        "",
        "出所: `data/questions/level3/writing_questions.txt`（保管用・公開登録しない）",
        "",
        "形式（2024年度〜）: **Eメール**（下線部2問・15〜25語）＋ **意見論述**（25〜35語）。",
        "",
        f"- 総問数: **{len(writing)}**（Eメール {len(emails)} / 意見論述 {len(opinions)}）",
        "",
        "---",
        "",
        "## 1. Eメール：下線質問の型",
        "",
        "| 疑問の型 | 件数 |",
        "|----------|------|",
    ]
    for k, v in wh_c.most_common():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## 2. 意見論述：QUESTION の型",
        "",
        "| 型 | 出題 No |",
        "|----|---------|",
        "| Which A or B | Q2, Q13 |",
        "| What … | Q4, Q19 |",
        "| Do you like / enjoy … | Q6, Q8, Q11, Q15, Q17, Q22 |",
        "",
        "---",
        "",
        "## 3. 全問台帳",
        "",
        "| No | 型 | 聞かれていること | 話題の手がかり |",
        "|----|----|------------------|----------------|",
    ]
    for w in writing:
        if w["kind"] == "Eメール":
            asked = " / ".join(w["underlines"])
            topic = w["topic"].replace("|", "\\|") or "（メール本文の話題に答える）"
        else:
            asked = w["question"]
            topic = "意見＋理由"
        asked = asked.replace("|", "\\|")
        lines.append(f"| Q{w['n']} | {w['kind']} | {asked} | {topic} |")

    lines += [
        "",
        "## 4. 求められる力（共通）",
        "",
        "| 型 | 求められること |",
        "|----|----------------|",
        "| Eメール | 下線の**2問両方**に英文で答える。語数目安 15〜25。時制・数・場所などを質問に合わせる |",
        "| 意見論述 | 意見を明示し、理由を書く（定番は意見1文＋理由）。語数目安 25〜35 |",
        "",
        "## 5. オリジナル網羅チェック用メモ",
        "",
        "- 下線は when/where/what/which/who/how many/how often/how did you feel/did … の組み合わせを意識。",
        "- 意見は Do you like〜 に偏りやすいので、Which / What / favorite も混ぜる。",
        "",
    ]
    (OUT / "writing.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_speaking() -> None:
    text = (DATA / "speaking_questions.txt").read_text(encoding="utf-8")
    speaking = []
    for m in re.finditer(r"問題(\d+):\s*(.*?)(?=\n---|\Z)", text, re.S):
        n = int(m.group(1))
        body = m.group(2)
        title_m = re.search(r"【Title】\s*\n(.+)", body)
        qs = re.findall(r"(\d+)\.\s*\[(passage|illustration|personal)\]\s*(.+)", body)
        speaking.append(
            {
                "n": n,
                "title": title_m.group(1).strip() if title_m else "",
                "questions": [
                    {"i": int(a), "type": b, "q": c.strip()} for a, b, c in qs
                ],
            }
        )

    def count_type(t: str) -> int:
        return sum(1 for s in speaking for q in s["questions"] if q["type"] == t)

    lines = [
        "# 3級公式保管：スピーキングで実際に聞かれていること",
        "",
        "出所: `data/questions/level3/speaking_questions.txt`（保管用・公開登録しない）",
        "",
        "形式: 約30語パッセージ（黙読・音読）→ **内容1** → **イラスト2** → カード裏返し → **自分のこと2**（3級配分）。",
        "",
        f"- カード数: **{len(speaking)}**（各カード質問5）",
        "",
        "---",
        "",
        "## 1. 質問タイプの内訳（全カード合計）",
        "",
        "| タイプ | 役割 | 件数 |",
        "|--------|------|------|",
        f"| [passage] | 本文の内容 | {count_type('passage')} |",
        f"| [illustration] | イラスト描写（多くは現在進行形） | {count_type('illustration')} |",
        f"| [personal] | 受験者自身 | {count_type('personal')} |",
        "",
        "## 2. トピック一覧",
        "",
        "| No | タイトル | 内容問 | イラスト問の焦点 | パーソナル問 |",
        "|----|----------|--------|------------------|--------------|",
    ]
    for s in speaking:
        pq = next(q["q"] for q in s["questions"] if q["type"] == "passage")
        ill = " / ".join(q["q"] for q in s["questions"] if q["type"] == "illustration")
        per = " / ".join(q["q"] for q in s["questions"] if q["type"] == "personal")
        lines.append(f"| Q{s['n']} | {s['title']} | {pq} | {ill} | {per} |")

    lines += [
        "",
        "## 3. 全問台帳（カード×質問）",
        "",
        "| カード | No | タイプ | 質問 |",
        "|--------|----|--------|------|",
    ]
    for s in speaking:
        for q in s["questions"]:
            lines.append(
                f"| Q{s['n']} {s['title']} | {q['i']} | {q['type']} | {q['q']} |"
            )

    lines += [
        "",
        "## 4. オリジナル網羅チェック用メモ",
        "",
        "- 配分を崩さない: **内容1 + イラスト2 + 自分2**。",
        "- イラストは What is X doing? / What is X looking at? が定番（進行形）。",
        "- パーソナルは Do you …? / Have you ever …? / What do you like …? / Can you …? / How do you …?。",
        "",
    ]
    (OUT / "speaking.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reading() -> None:
    text = (DATA / "reading_comprehesion_questions.txt").read_text(encoding="utf-8")
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
        reading.append(
            {"passage": pnum, "title": title, "type": ptype, "questions": qs}
        )

    fc = Counter(q["focus"] for r in reading for q in r["questions"])
    lines = [
        "# 3級公式保管：読解で実際に聞かれていること",
        "",
        "出所: `data/questions/level3/reading_comprehesion_questions.txt`（保管用・公開登録しない）",
        "",
        "形式: **掲示2問 + メール3問 + 物語・説明文5問** のセット構成（本ファイルは6セット相当・本文18・設問60）。",
        "",
        f"- 本文数: **{len(reading)}** / 設問数: **{sum(len(r['questions']) for r in reading)}**",
        f"- 掲示・案内: {sum(1 for r in reading if r['type']=='掲示・案内')} / "
        f"メール: {sum(1 for r in reading if r['type']=='メール')} / "
        f"物語・説明文: {sum(1 for r in reading if r['type']=='物語・説明文')}",
        "",
        "---",
        "",
        "## 1. パッセージ型と設問数",
        "",
        "| 本文 | 型 | タイトル | 設問数 |",
        "|------|----|----------|--------|",
    ]
    for r in reading:
        lines.append(
            f"| 本文{r['passage']} | {r['type']} | {r['title']} | {len(r['questions'])} |"
        )

    lines += [
        "",
        "## 2. 設問の焦点",
        "",
        "| 焦点 | 件数 |",
        "|------|------|",
    ]
    for k, v in fc.most_common():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## 3. 物語・説明文でよくある末尾設問",
        "",
        "- `What is this story about?` / `What is this story mainly about?`（要旨）が各物語にほぼ付く。",
        "",
        "---",
        "",
        "## 4. 全問台帳",
        "",
        "| 本文 | 型 | 設問 | 焦点 | 質問 | 正解 |",
        "|------|----|------|------|------|------|",
    ]
    for r in reading:
        for q in r["questions"]:
            qq = q["q"].replace("|", "\\|")
            aa = q["ans"].replace("|", "\\|")
            if len(qq) > 70:
                qq = qq[:67] + "…"
            if len(aa) > 50:
                aa = aa[:47] + "…"
            lines.append(
                f"| 本文{r['passage']} | {r['type']} | {q['id']} | {q['focus']} | {qq} | {aa} |"
            )

    lines += [
        "",
        "## 5. オリジナル網羅チェック用メモ",
        "",
        "- セット構成（掲示2・メール3・物語5）を崩さない。",
        "- 掲示: 日時・場所・持ち物・色分け・主催者の行為など**対応表・条件**を読ませる。",
        "- メール: 依頼・予定・過去の共有体験・相手へのお願い。",
        "- 物語: 細部＋理由＋**要旨（What is this story about?）**。",
        "",
    ]
    (OUT / "reading_comprehension.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_readme() -> None:
    readme = """# 公式保管問題の出題内容インベントリ

`data/questions/`（級別 txt）で**実際に聞かれていること**を級・カテゴリごとに整理した台帳。  
オリジナル作問の網羅チェック用。公式文面の転載・公開登録用ではない。

## 構成

```
docs/inventory/
  level3/
    grammar_vocabulary.md      # 文法・語彙
    conversation.md            # 会話補充
    listening_illustration.md  # L第1部（応答）
    listening_conversation.md  # L第2部（会話）
    listening_passage.md       # L第3部（モノローグ）
    reading_comprehension.md   # 読解
    writing.md                 # ライティング
    speaking.md                # スピーキング
  level4/                      # （未作成）
  level5/                      # （未作成）
```

| 級 | 状態 |
|----|------|
| 3級 | [`level3/`](level3/) 全カテゴリ（公式保管にあるもの） |
| 4級 | 未作成 |
| 5級 | 未作成 |

### 3級メモ

- 公式保管に **語順（wordorder）ファイルはない**（オリジナル側のみ）。
- 読解ファイル名の typo `reading_comprehesion` はデータ側の既存名に合わせている。
"""
    (ROOT / "docs" / "inventory" / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    li = parse_listening(DATA / "listening_illustration_questions.txt")
    lc = parse_listening(DATA / "listening_conversation_questions.txt")
    lp = parse_listening(DATA / "listening_passage_questions.txt")
    assert len(li) == 50 and len(LI_FN) == 50
    assert len(lc) == 50 and len(lp) == 50

    write_listening_illustration(li)
    write_listening_qa(
        "listening_conversation_questions.txt",
        "リスニング第2部（会話内容一致）",
        "やや長い会話を聞き、内容一致の4択。",
        lc,
        [
            "ひっかけは「会話に出たが質問の答えではない情報」（例: 妹の話が出ても探しているのは本人）。",
            "what（問題・予定）と when / where / why のバランスを公開セットでも意識する。",
        ],
        [
            ("困りごと・問題", "What is the problem? / What is X’s problem?"),
            ("依頼・頼みごと", "What does X ask Y to do?"),
            ("予定・これから", "What will X do …? / When will they …?"),
            ("場所・集合", "Where will they meet? / Where is the meeting?"),
            ("理由", "Why can’t / Why did …?"),
            ("人物", "Who is … looking for? / Who will pick … up?"),
            ("好み・クラブ・科目", "Which club / Which subject / What does X like"),
            ("値段・期間・頻度", "How much / How long / When does X usually"),
        ],
    )
    write_listening_qa(
        "listening_passage_questions.txt",
        "リスニング第3部（文・モノローグ内容一致）",
        "1人の短いモノローグを聞き、内容一致の4択。",
        lp,
        [
            "モノローグ内の**複数の数字・予定**から、質問が指す1点だけを取る練習が中心。",
            "「すでに得意／昔やっていた」と「これから挑戦」の取り違えが典型ひっかけ。",
        ],
        [
            ("これからすること", "What is X going to do / What will …"),
            ("回数・期間・年齢・数量", "How many times / How long / How old / How many"),
            ("時刻・曜日・開閉", "When does … close/open / When will it rain"),
            ("場所・勤務地・留学先", "Where does X live/work/study"),
            ("理由", "Why was X late / Why is X taking …"),
            ("受け取った物・忘れた物", "What did X get/receive/forget"),
            ("話題の特定", "What is the girl talking about?"),
            ("話し手の場所", "Where is the woman talking?"),
        ],
    )
    write_writing()
    write_speaking()
    write_reading()
    update_readme()
    print("done:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
