#!/usr/bin/env python3
"""
英検5級の過去問PDF（問題冊子・解答F日程・リスニング原稿）から
data/questions/level5/*.txt を生成する。
"""
from __future__ import annotations

import re
from pathlib import Path

import fitz

_REPO = Path(__file__).resolve().parents[1]
_PDF = _REPO / 'data' / 'pdf_import' / 'level5_kakomon'
_OUT = _REPO / 'data' / 'questions' / 'level5'

ROUNDS = (
    {
        'exam_pdf': '2025-2-1ji-5kyu.pdf',
        'script_pdf': '2025-2-1ji-5kyu_script.pdf',
        'answer_pdf': '202502F5kyu_answers.pdf',
    },
    {
        'exam_pdf': '2025-3-1ji-5kyu.pdf',
        'script_pdf': '2025-3-1ji-5kyuscript.pdf',
        'answer_pdf': '202503F5kyu_answers.pdf',
    },
    {
        'exam_pdf': '2026-1-1ji-5kyu.pdf',
        'script_pdf': '2026-1-1ji_5kyuscript.pdf',
        'answer_pdf': '202601F5kyu_answers.pdf',
    },
)


def pdf_text(path: Path) -> str:
    return ''.join(page.get_text() for page in fitz.open(path))


def normalize_ws(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def clean_japanese(text: str) -> str:
    return re.sub(r'(?<=[ぁ-んァ-ン一-龥])\s+(?=[ぁ-んァ-ン一-龥])', '', text)


def parse_answers(answer_pdf: str) -> tuple[dict[int, int], dict[int, int]]:
    text = pdf_text(_PDF / answer_pdf)
    reading: dict[int, int] = {}
    for mo in re.finditer(r'\((\d+)\)\s*(\d)', text):
        n, a = int(mo.group(1)), int(mo.group(2))
        if 1 <= n <= 25:
            reading[n] = a
    listening: dict[int, int] = {}
    section = re.search(r'5級リスニング(.*)', text, re.DOTALL)
    if section:
        for mo in re.finditer(r'No\.\s*(\d+)\s*(\d)', section.group(1)[:4000]):
            listening[int(mo.group(1))] = int(mo.group(2))
    return reading, listening


def _is_grammar_instruction_body(body: str) -> bool:
    head = body[:80]
    return 'までの' in head and 'A :' not in head


def parse_grammar_blocks(exam_text: str) -> dict[int, dict]:
    text = normalize_ws(exam_text)
    results: dict[int, dict] = {}
    for n in range(1, 16):
        pattern = rf'\({n}\)\s*(.*?)\s+1\s+(\S+)\s+2\s+(\S+)\s+3\s+(\S+)\s+4\s+(\S+)'
        chosen = None
        chosen_body = ''
        for mo in re.finditer(pattern, text):
            body = mo.group(1).strip()
            if _is_grammar_instruction_body(body):
                am = re.search(r'A\s*:.+', body)
                if am:
                    body = am.group(0).strip()
                else:
                    em = re.search(r'(?:Mr\.|Ms\.|Mrs\.|I\s[A-Z]|[A-Z][a-z].+?)\s*.+?\(\s*\).+', body)
                    if em:
                        body = em.group(0).strip()
                    else:
                        continue
            if 'Listening Test' in body:
                continue
            if len(body) < 15:
                continue
            chosen = mo
            chosen_body = body
        if chosen is None:
            direct_pattern = (
                rf'\({n}\)\s*(.+?\(\s*\).+?)\s+1\s+(\S+)\s+2\s+(\S+)\s+3\s+(\S+)\s+4\s+(\S+)'
            )
            for direct in re.finditer(direct_pattern, text):
                body = direct.group(1).strip()
                if _is_grammar_instruction_body(body):
                    continue
                chosen = direct
                chosen_body = body
                break
        if chosen is None:
            continue
        results[n] = {
            'text': chosen_body,
            'choices': [chosen.group(i) for i in range(2, 6)],
        }
    return results


def parse_conversation_blocks(exam_text: str) -> dict[int, dict]:
    text = re.sub(r'[ \t]+', ' ', exam_text)
    text = re.sub(r'\n+', '\n', text)
    results: dict[int, dict] = {}
    speaker = r'(?:Boy|Girl|Mother|Father|Man|Woman|Teacher|Customer|Waiter|Girl\s+\d+|A|B)\s*:'
    for n in range(16, 21):
        pattern = rf'\({n}\)\s*({speaker}[\s\S]+?)\s+1\s+(.+?)\s+2\s+(.+?)\s+3\s+(.+?)\s+4\s+(.+?)(?=\(\d+\)|Grade|Listening|$)'
        mo = re.search(pattern, text, re.DOTALL)
        if not mo:
            continue
        body = re.sub(r'\s+', ' ', mo.group(1)).strip()
        choices = [re.sub(r'\s+', ' ', mo.group(i)).strip() for i in range(2, 6)]
        results[n] = {'text': body, 'choices': choices}
    return results


def parse_wordorder_blocks(exam_text: str) -> dict[int, dict]:
    text = normalize_ws(exam_text)
    results: dict[int, dict] = {}
    for mo in re.finditer(
        r'\((\d+)\)\s*([^()]+?)\(\s*(①[^)]+)\)\s*1\s*番目\s*3\s*番目\s*(.*?)\s+'
        r'1\s+([①②③④]\s*─\s*[①②③④])\s+2\s+([①②③④]\s*─\s*[①②③④])\s+'
        r'3\s+([①②③④]\s*─\s*[①②③④])\s+4\s+([①②③④]\s*─\s*[①②③④])',
        text,
    ):
        n = int(mo.group(1))
        if not (21 <= n <= 25):
            continue
        jp = clean_japanese(mo.group(2).strip())
        if 'までの日' in jp or '本ぶん文' in jp.replace(' ', ''):
            continue
        chips = mo.group(3).strip()
        en_tail = mo.group(4).strip()
        results[n] = {
            'text': f'{jp}\n{chips}\n( ) [1番目] ( ) [3番目] {en_tail}',
            'choices': [mo.group(i).strip() for i in range(5, 9)],
        }
    return results


def parse_listening_part1(script_text: str) -> dict[int, dict]:
    results: dict[int, dict] = {}
    blocks = re.split(r'(?=☆☆\s*No\.\s*\d+)', script_text)
    for block in blocks:
        mo = re.search(r'No\.\s*(\d+)\s*(.*)', block, re.DOTALL)
        if not mo:
            continue
        n = int(mo.group(1))
        if not (1 <= n <= 10):
            continue
        dialog: list[str] = []
        choices: list[str] = []
        for ln in [l.strip() for l in mo.group(2).splitlines() if l.strip()]:
            if re.match(r'^[★☆]\d', ln):
                choices.append(re.sub(r'^[☆★]\d\s*', '', ln).strip())
            elif re.match(r'^[★☆]', ln):
                dialog.append(ln)
        if len(choices) < 3:
            continue
        results[n] = {'dialog': '\n'.join(dialog), 'choices': choices[:3]}
    return results


def parse_listening_part2(script_text: str, exam_text: str) -> dict[int, dict]:
    results: dict[int, dict] = {}
    exam_norm = normalize_ws(exam_text)
    for n in range(11, 16):
        cm = re.search(
            rf'No\.\s*{n}\s+1\s+(.+?)\s+2\s+(.+?)\s+3\s+(.+?)\s+4\s+(.+?)(?=No\.\s*\d+|第|$)',
            exam_norm,
        )
        if not cm:
            continue
        choices = [cm.group(i).strip() for i in range(1, 5)]
        sm = re.search(rf'☆☆\s*No\.\s*{n}\s*(.*?)(?=☆☆\s*No\.\s*\d+|$)', script_text, re.DOTALL)
        if not sm:
            continue
        body = sm.group(1)
        qm = re.search(r'Question:\s*(.+)', body, re.IGNORECASE)
        if not qm:
            continue
        dialog_lines = [
            ln.strip()
            for ln in body.split('Question:')[0].splitlines()
            if ln.strip() and re.match(r'^[★☆]', ln.strip())
        ]
        results[n] = {
            'dialog': '\n'.join(dialog_lines),
            'question': qm.group(1).strip(),
            'choices': choices,
        }
    return results


def _trim_listening_choice(text: str) -> str:
    text = text.strip()
    for marker in ('では、時間', '公正なる', '試験監督者', '受験者'):
        idx = text.find(marker)
        if idx > 0:
            text = text[:idx].strip()
    return text.split('\n')[0].strip()


def parse_listening_part3(script_text: str) -> dict[int, dict]:
    results: dict[int, dict] = {}
    for mo in re.finditer(
        r'No\.\s*(\d+)\s*[★☆]1\s*(.+?)\s*[★☆]2\s*(.+?)\s*[★☆]3\s*(.+?)(?=☆☆\s*No\.\s*\d+|$)',
        script_text,
        re.DOTALL,
    ):
        n = int(mo.group(1))
        if not (16 <= n <= 25):
            continue
        results[n] = {
            'choices': [_trim_listening_choice(mo.group(i)) for i in range(2, 5)],
        }
    return results


def grammar_explanation(choices: list[str], correct_idx: int) -> str:
    correct = choices[correct_idx - 1]
    wrong = [c for i, c in enumerate(choices, 1) if i != correct_idx]
    wrong_text = '」「'.join(wrong)
    return (
        f'正解は「{correct}」です。文脈に最も合う語句を選びます。\n'
        f'他の選択肢「{wrong_text}」は、この空所や会話の流れには合いません。'
    )


def conversation_explanation(choices: list[str], correct_idx: int) -> str:
    correct = choices[correct_idx - 1]
    wrong = [c for i, c in enumerate(choices, 1) if i != correct_idx]
    wrong_text = '」「'.join(wrong)
    return (
        f'会話の流れから、空所に入る最も自然なのは「{correct}」です。\n'
        f'「{wrong_text}」は前後の発話とつながりが不自然です。'
    )


def wordorder_explanation(choices: list[str], correct_idx: int) -> str:
    return (
        f'正しい語順の組み合わせは「{choices[correct_idx - 1]}」です。\n'
        f'日本文の意味になるよう、1番目と3番目に来る語句の組み合わせを選びます。'
    )


def listening_p1_explanation(choices: list[str], correct_idx: int) -> str:
    correct = choices[correct_idx - 1]
    return (
        f'会話の最後の発話に対する自然な応答は「{correct}」です。\n'
        f'他の選択肢は質問や発話の内容と合いません。'
    )


def listening_p2_explanation(question: str, correct_text: str) -> str:
    return (
        f'質問「{question}」に対する正しい答えは「{correct_text}」です。\n'
        f'会話の内容をよく聞いて選びます。'
    )


def listening_p3_explanation(choices: list[str], correct_idx: int) -> str:
    correct = choices[correct_idx - 1]
    return (
        f'放送された英文の内容に最も合うのは選択肢{correct_idx}「{correct}」です。\n'
        f'イラストの動作・状況と英文の意味を照らし合わせて選びます。'
    )


def load_round(cfg: dict):
    exam = pdf_text(_PDF / cfg['exam_pdf'])
    script = pdf_text(_PDF / cfg['script_pdf'])
    answers_r, answers_l = parse_answers(cfg['answer_pdf'])
    return {
        'grammar': parse_grammar_blocks(exam),
        'conversation': parse_conversation_blocks(exam),
        'wordorder': parse_wordorder_blocks(exam),
        'listen_p1': parse_listening_part1(script),
        'listen_p2': parse_listening_part2(script, exam),
        'listen_p3': parse_listening_part3(script),
        'answers_r': answers_r,
        'answers_l': answers_l,
    }


def build_files(rounds: list[dict]) -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    grammar_blocks: list[str] = []
    conv_blocks: list[str] = []
    word_blocks: list[str] = []
    illust_blocks: list[str] = []
    conv_listen_blocks: list[str] = []

    gnum = cnum = wnum = p1num = p2num = 0
    p3num = 30

    for rnd in rounds:
        for n in range(1, 16):
            gnum += 1
            item = rnd['grammar'][n]
            ans = rnd['answers_r'][n]
            choices = item['choices']
            grammar_blocks.append(
                f'問題{gnum}:\n{item["text"]}\n\n'
                f'選択肢{gnum}:\n'
                + '\n'.join(f'{i}. {c}' for i, c in enumerate(choices, 1))
                + f'\n\n【正解{gnum}】\n{ans}. {choices[ans - 1]}\n\n'
                f'【解説{gnum}】\n{grammar_explanation(choices, ans)}\n'
            )

        for n in range(16, 21):
            cnum += 1
            item = rnd['conversation'][n]
            ans = rnd['answers_r'][n]
            choices = item['choices']
            conv_blocks.append(
                f'問題{cnum}:\n{item["text"]}\n\n'
                f'選択肢{cnum}:\n'
                + '\n'.join(f'{i}. {c}' for i, c in enumerate(choices, 1))
                + f'\n\n【正解{cnum}】\n{ans}. {choices[ans - 1]}\n\n'
                f'【解説{cnum}】\n{conversation_explanation(choices, ans)}\n'
            )

        for n in range(21, 26):
            wnum += 1
            item = rnd['wordorder'][n]
            ans = rnd['answers_r'][n]
            choices = item['choices']
            word_blocks.append(
                f'問題{wnum}:\n{item["text"]}\n\n'
                f'選択肢{wnum}:\n'
                + '\n'.join(f'{i}. {c}' for i, c in enumerate(choices, 1))
                + f'\n\n【正解{wnum}】\n{ans}. {choices[ans - 1]}\n\n'
                f'【解説{wnum}】\n{wordorder_explanation(choices, ans)}\n'
            )

        for n in range(1, 11):
            p1num += 1
            item = rnd['listen_p1'][n]
            ans = rnd['answers_l'][n]
            choices = item['choices']
            illust_blocks.append(
                f'No.{p1num}:\n{item["dialog"]}\n\n'
                f'Question No.{p1num}:\n'
                + '\n'.join(f'{i}. {c}' for i, c in enumerate(choices, 1))
                + f'\n\n【正解{p1num}】\n{ans}. {choices[ans - 1]}\n\n'
                f'【解説{p1num}】\n{listening_p1_explanation(choices, ans)}\n'
            )

        for n in range(11, 16):
            p2num += 1
            item = rnd['listen_p2'][n]
            ans = rnd['answers_l'][n]
            choices = item['choices']
            conv_listen_blocks.append(
                f'No.{p2num}:\n{item["dialog"]}\n\n'
                f'Question No.{p2num}:\n{item["question"]}\n\n'
                + '\n'.join(f'{i}. {c}' for i, c in enumerate(choices, 1))
                + f'\n\n【正解{p2num}】\n{ans}. {choices[ans - 1]}\n\n'
                f'【解説{p2num}】\n{listening_p2_explanation(item["question"], choices[ans - 1])}\n'
            )

        for n in range(16, 26):
            p3num += 1
            item = rnd['listen_p3'][n]
            ans = rnd['answers_l'][n]
            choices = item['choices']
            illust_blocks.append(
                f'No.{p3num}:\n(イラスト一致問題)\n\n'
                f'Question No.{p3num}:\n'
                + '\n'.join(f'{i}. {c}' for i, c in enumerate(choices, 1))
                + f'\n\n【正解{p3num}】\n{ans}. {choices[ans - 1]}\n\n'
                f'【解説{p3num}】\n{listening_p3_explanation(choices, ans)}\n'
            )

    def write(name: str, blocks: list[str]) -> None:
        path = _OUT / name
        path.write_text('\n---\n\n'.join(blocks), encoding='utf-8')
        print(f'Wrote {path} ({len(blocks)} items)')

    write('grammar_fill_questions.txt', grammar_blocks)
    write('conversation_questions.txt', conv_blocks)
    write('wordorder_questions.txt', word_blocks)
    write('listening_illustration_questions.txt', illust_blocks)
    write('listening_conversation_questions.txt', conv_listen_blocks)


def main() -> int:
    rounds = []
    for cfg in ROUNDS:
        rnd = load_round(cfg)
        for key in ('grammar', 'conversation', 'wordorder', 'listen_p1', 'listen_p2', 'listen_p3'):
            expected = 15 if key == 'grammar' else 5 if key in ('conversation', 'listen_p2') else 10 if 'p1' in key or 'p3' in key else 5
            if key == 'wordorder':
                expected = 5
            if key == 'listen_p3':
                expected = 10
            got = len(rnd[key])
            if got != expected:
                missing = set(range(1, expected + 1)) - set(rnd[key])
                if key == 'conversation':
                    missing = set(range(16, 21)) - set(rnd[key])
                elif key == 'wordorder':
                    missing = set(range(21, 26)) - set(rnd[key])
                elif key == 'listen_p2':
                    missing = set(range(11, 16)) - set(rnd[key])
                elif key == 'listen_p3':
                    missing = set(range(16, 26)) - set(rnd[key])
                raise ValueError(f'{cfg["exam_pdf"]} {key}: expected {expected}, got {got}, missing {missing}')
        rounds.append(rnd)
    build_files(rounds)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
