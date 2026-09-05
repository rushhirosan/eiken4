#!/usr/bin/env python3
"""Insert 【ポイントN】 blocks into original listening question txt files.

現状は 3級のみ。4・5級は 3級で確認後に DATA へ追加する。
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

Point = tuple[str, list[str]]  # (title, keys)


def _p(title: str, *keys: str) -> Point:
    return (title, list(keys))


# --- Level 3 listening_illustration ---
L3_ILL: dict[int, Point] = {
    1: _p(
        'Where could it be? には場所で答える',
        '場所を聞くときは on / by / at + 名詞',
        '天気や買ったものは場所の答えではない',
    ),
    2: _p(
        '手伝いの依頼には OK + 行動で返す',
        "Could you help 〜? → OK. I'll carry / take 〜",
        '場所が決まったあとは there などで受ける',
    ),
    3: _p(
        'How did you feel? には I felt 〜 で気持ち',
        'How did you feel? / How do you feel?',
        '日程や他人の様子は気持ちの答えではない',
    ),
    4: _p(
        'Can you buy 〜? には OK + 買いに行く',
        "Can you buy them? → OK. I'll go to 〜",
        'パーティーの開始時刻は依頼への返事ではない',
    ),
    5: _p(
        'Where can we 〜? には提案 We can 〜',
        'where can we practice → We can use 〜',
        '床の状態など場所以外の描写に惑わされない',
    ),
    6: _p(
        'Any ideas? には How about 〜 で提案',
        'プレゼントの相談 → How about a small 〜?',
        '誕生日の日付だけでは提案にならない',
    ),
    7: _p(
        'What should we do? には具体的な行動',
        "Let's call 〜 / Ask 〜 など次の一手",
        'バスの色や待ち時間だけでは行動の答えではない',
    ),
    8: _p(
        'When will you 〜? には時期・期限で答える',
        'Maybe by this weekend. / By Friday.',
        '雑誌の厚さなど内容の説明は時期ではない',
    ),
    9: _p(
        'What do you want? には注文 Some 〜, please.',
        '食べ物・飲み物 → Some hot noodles, please.',
        '部活の感想は注文の答えではない',
    ),
    10: _p(
        '写真の指示には OK + 短い合図',
        'Smile, everyone! / OK. など',
        '桜の色など景色の説明は返事にならない',
    ),
    11: _p(
        'What should I do? には Ask / Check など',
        '落とし物 → Ask 〜 if anyone found it.',
        '置き場所の説明だけでは行動の答えではない',
    ),
    12: _p(
        '場所変更の提案には OK + 伝える',
        "move the meeting → OK. I'll tell 〜",
        'テントの場所だけでは返事にならない',
    ),
    13: _p(
        'What did you buy? には買ったもの',
        'What did you buy? → A set of 〜 / Some 〜',
        '値段や店の名前だけでは「何を買ったか」にならない',
    ),
    14: _p(
        'How long will 〜? には Until 〜 / For 〜',
        "How long will the meeting last? → Until four o'clock.",
        '好みの理由（Because I like 〜）は長さの答えではない',
    ),
    15: _p(
        'うまくいかないときは別のものを使う',
        "What should I do if 〜? → Use the one in 〜",
        '機械の場所の説明と「代わりに使うもの」を混同しない',
    ),
    16: _p(
        'Who 〜? には人で答える',
        'Who taught you? → My cousin / My teacher.',
        'いつ覚えたか（last spring）は人の答えではない',
    ),
    17: _p(
        'What if 〜? には代わり Use 〜 instead',
        'What if the gloves are too big? → Use a dry towel instead.',
        '道具の場所だけでは「代わり」の答えにならない',
    ),
    18: _p(
        'When will you rest? には After 〜 / Before 〜',
        'After I take this 〜 to the office.',
        '新聞の用途は休息の時刻ではない',
    ),
    19: _p(
        'What should we bring? には持ち物を列挙',
        'just in case → A small light and some spray.',
        'クラブの場所は持ち物の答えではない',
    ),
    20: _p(
        'How is he now? には状態 He\'s fine.',
        "How is he? → He's fine. / He only needed 〜",
        '部活の場所はけがの状態の答えではない',
    ),
}

# --- Level 3 listening_conversation ---
L3_CONV: dict[int, Point] = {
    1: _p('Where 〜? は会話の行き先キーワード', 'pick it up / go to 〜 → 店・場所', '予備の日時（日曜・4時）は本命ではない'),
    2: _p('When should 〜? は before / by / until', 'return 〜 before lunch', '宿題の速さ・午後の用途は返す時刻ではない'),
    3: _p('Why 〜? は Because + 理由', 'Why boots? → Because 〜 walk through wet grass', 'クラブ名・雨の予定は理由ではない'),
    4: _p('What will 〜 do to help? は具体的な作業', 'help → grate / carry / wash など動詞', '時間・場所だけでは「何をするか」にならない'),
    5: _p('What still need to do? は finish / complete', 'still need → Finish 〜 tonight', '道具の場所は残りの宿題ではない'),
    6: _p('How long has 〜? は Since / For', 'play the violin → Since she was eight', '練習場所は期間の答えではない'),
    7: _p('What will they do if 〜? は if 節の予定', 'if it rains → visit the indoor pool', '晴れの日の予定は if の答えではない'),
    8: _p('Why tell not to worry? は Because + 安心材料', 'not to worry → Because he has practiced a lot', '開始時刻だけでは理由にならない'),
    9: _p('How can 〜 get to 〜? は道順', 'Go past 〜 and turn right at 〜', '距離・時間だけでは行き方にならない'),
    10: _p('Do you mind if 〜? は Not at all. / Of course not.', 'open the window → Not at all. It is a little hot.', '窓の場所の説明は許可の返事ではない'),
    11: _p('Why bring 〜? は Because + 必要な理由', 'bring a compass → Because the path isn\'t marked', '地図の大きさは理由ではない'),
    12: _p('What must they do before 〜? は before の条件', 'before class → Finish the math worksheet', '教室の場所は事前準備の答えではない'),
    13: _p('How many times has 〜? は回数', 'Twice. / Three times.', '道具の名前だけでは回数にならない'),
    14: _p('Why is 〜 heavy? は Because + 中身', 'heavy backpack → Because she brought extra batteries', '色や大きさだけでは理由にならない'),
    15: _p('Under what condition? は If 〜', 'use the kitchen → If she washes every dish afterward', '料理名だけでは条件の答えではない'),
    16: _p('How long has 〜 collected? は For about 〜', 'collected postcards → For about two years', '最初の1枚の話は期間の答えではない'),
    17: _p('When can they 〜? は If 〜 is empty', 'borrow chairs → If the English room is empty', '椅子の色は借りられる条件ではない'),
    18: _p('Why bring empty jars? は Because they will 〜', 'empty jars → Because they will paint them', '店の場所は理由ではない'),
    19: _p('How many times has 〜 taken? は回数', 'night bus → Three times.', 'バスの時刻表だけでは回数にならない'),
    20: _p('When can they 〜? は Only if 〜', 'practice on the roof → Only if no one is taking photos', '楽器の種類は条件の答えではない'),
}

# --- Level 3 listening_passage ---
L3_PASS: dict[int, Point] = {
    1: _p('Where will 〜? は work / visit + at 〜', 'Where will 〜 work? → At 〜 / In 〜', '持ち帰りたいもの・後でしたいことは場所ではない'),
    2: _p('What did 〜 teach? は taught + 内容', 'taught 〜 how to 〜 / how to use 〜', 'お礼や食事は「教えた内容」ではない'),
    3: _p('Why did 〜 wake up early? は to 不定詞の目的', 'woke up early to 〜（目的）', '他人の手伝いは本人の目的と混同しない'),
    4: _p('What want to write about? は write about 〜', 'write a report about 〜 / about 〜', '日付だけではテーマにならない'),
    5: _p('What did 〜 do after 〜? は after の行動', 'after 〜, he/she 過去形', '練習の内容だけでは after の行動ではない'),
    6: _p('How long has 〜 lived? は For 〜 / Since 〜', 'How long has 〜? → For three years.', '好み・特徴の描写は期間ではない'),
    7: _p('How many times has 〜? は回数', 'Twice. / Three times. / Four times.', '天気・場所の説明は回数ではない'),
    8: _p('What still need to do? は still need + 残り', 'still need to 〜 / Add 〜', '締切の日だけでは残りの作業ではない'),
    9: _p('What will 〜 do if 〜? は if 節', 'if it snows / if it rains → そのときの行動', '晴れの日の予定は if の答えではない'),
    10: _p('How many times have they 〜? は回数', 'How many times → 数字 + times', '場所・道具の説明は回数ではない'),
    11: _p('Why will 〜 leave early? は Because + 理由', 'leave early because 〜', '時刻表だけでは理由にならない'),
    12: _p('How many times this year? は回数 + 期間', 'this year → Four times.', '場所の説明は回数ではない'),
    13: _p('How long has 〜 checked 〜? は For 〜', 'has checked 〜 for six months', '数値の結果だけでは期間ではない'),
    14: _p('Why stay after school? は To 〜 / Because 〜', 'stay after school to 〜', '帰宅時刻だけでは理由にならない'),
    15: _p('How many times this month? は回数', 'this month → Five times.', '道具名だけでは回数にならない'),
    16: _p('Why leave early? は Because + 理由', 'leave early because the traffic 〜', '到着時刻だけでは理由にならない'),
    17: _p('How long has 〜 studied 〜? は For 〜', 'studied 〜 for a year and a half', '好きな科目だけでは期間ではない'),
    18: _p('How many times this spring? は回数', 'this spring → Three times.', '場所の名前は回数ではない'),
    19: _p('Why skip 〜? は Because + 約束・理由', 'skip 〜 because he promised to 〜', '相手の名前だけでは理由にならない'),
    20: _p('How long lived in 〜? は For 〜', 'lived in 〜 for four years', '部屋の数だけでは期間ではない'),
}

DATA: dict[tuple[str, str], dict[int, Point]] = {
    ('3', 'listening_illustration'): L3_ILL,
    ('3', 'listening_conversation'): L3_CONV,
    ('3', 'listening_passage'): L3_PASS,
}


def format_point(number: int, point: Point) -> str:
    title, keys = point
    lines = [
        f'【ポイント{number}】',
        '種別: リスニング',
        f'見出し: {title}',
    ]
    for key in keys:
        lines.append(f'・{key}')
    return '\n'.join(lines)


def split_listening_blocks(content: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in content.split('\n'):
        if line.strip().startswith('No.') and current:
            blocks.append('\n'.join(current))
            current = [line]
        elif line.strip().startswith('No.'):
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append('\n'.join(current))
    return blocks


def block_number(block: str) -> int | None:
    m = re.search(r'No\.(\d+):', block)
    return int(m.group(1)) if m else None


def insert_points_into_file(path: Path, points: dict[int, Point], *, replace: bool = False) -> int:
    content = path.read_text(encoding='utf-8')
    blocks = split_listening_blocks(content)
    changed = 0
    out_blocks: list[str] = []
    for block in blocks:
        num = block_number(block)
        if num is None or num not in points:
            out_blocks.append(block.rstrip())
            continue
        if re.search(rf'【ポイント{num}】', block):
            if not replace:
                out_blocks.append(block.rstrip())
                continue
            block = re.sub(
                rf'\n*【ポイント{num}】.*?(?=\n---|\Z)',
                '',
                block,
                flags=re.DOTALL,
            ).rstrip()
        point_text = format_point(num, points[num])
        trimmed = block.rstrip()
        if trimmed.endswith('---'):
            trimmed = trimmed[:-3].rstrip()
        out_blocks.append(trimmed + '\n\n' + point_text)
        changed += 1
    new_content = '\n\n---\n\n'.join(out_blocks)
    if not new_content.endswith('\n'):
        new_content += '\n'
    path.write_text(new_content, encoding='utf-8')
    return changed


def main() -> None:
    import sys
    replace = '--replace' in sys.argv
    total = 0
    for (level, category), points in DATA.items():
        path = ROOT / f'data/questions/original/level{level}/{category}_questions.txt'
        if not path.exists():
            print(f'skip missing: {path}')
            continue
        n = insert_points_into_file(path, points, replace=replace)
        print(f'{path.relative_to(ROOT)}: inserted {n}')
        total += n
    print(f'total inserted: {total}')


if __name__ == '__main__':
    main()
