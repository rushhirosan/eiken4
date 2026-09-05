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


# --- Level 3 listening_illustration（イラスト：次の一言を選ぶ）---
# 見出し = 最後の問い／場面の型 → 答えの型。・1本目=使える英語、・2本目=ひっかけの型
L3_ILL: dict[int, Point] = {
    1: _p(
        'Where 〜? / Where could it be? には場所で答える',
        'on / by / at / next to + 場所の名詞',
        '天気・買ったものなど、場所以外の話は答えにならない',
    ),
    2: _p(
        '手伝いの依頼には「了解 + 行動」で返す',
        "Could you help 〜? → OK. I'll carry / take 〜",
        '場所が決まったら there などで受け、日時や物の説明だけで終わらない',
    ),
    3: _p(
        'How did you feel? には I felt 〜 で気持ち',
        'I felt happy / tired / relaxed. など感情の形容詞',
        '日程や他人の様子は気持ちの答えではない',
    ),
    4: _p(
        'Can you buy / get 〜? には「了解 + 買いに行く」',
        "OK. I'll go to the supermarket / store.",
        '開始時刻や物の色だけでは依頼への返事にならない',
    ),
    5: _p(
        'Where can we 〜? には代わりの場所を提案',
        'We can use / go to 〜（別の場所）',
        '閉じた理由や感想だけでは場所の答えではない',
    ),
    6: _p(
        'Any ideas? には How about 〜? で提案',
        'How about a 〜? / Why don\'t we 〜?',
        '誕生日や世話の説明だけでは提案にならない',
    ),
    7: _p(
        'What should we do? には次の一手を提案',
        "Let's call / ask / go to 〜",
        '色・好み・待ち時間だけでは行動の答えではない',
    ),
    8: _p(
        'When will you 〜? には時期・期限で答える',
        'by this weekend / on Friday / after 〜',
        '物の厚さや借りた相手は時期の答えではない',
    ),
    9: _p(
        'What do you want? にはほしいもの・注文で答える',
        'Some 〜, please. / I\'d like 〜.',
        '直前の出来事の感想や閉店時間は注文ではない',
    ),
    10: _p(
        '撮影の準備が終わったら撮る人の短い合図',
        'OK. / Smile! / Ready? など次の動作の一言',
        '景色や試合結果など、いま撮る流れと関係ない説明は続きにならない',
    ),
    11: _p(
        'What should I do? には具体的な行動で答える',
        'Ask 〜 / Check 〜 / Call 〜 など次にすること',
        '置き場所や時刻の説明だけでは「どうするか」にならない',
    ),
    12: _p(
        '提案を受けたら「了解 + 次の一手」で返す',
        "OK. I'll tell / call / bring 〜",
        '話題に出た物の場所や好みだけでは返事にならない',
    ),
    13: _p(
        'What did you buy? には買ったものそのもので答える',
        'A set of 〜 / Some 〜 / A 〜',
        '開店時刻や行く頻度は「何を買ったか」ではない',
    ),
    14: _p(
        'How long will 〜 last? には長さ・終了で答える',
        'Until 〜 / For 〜 hours / About 〜 minutes',
        '持ち物の理由や過去の作業は長さの答えではない',
    ),
    15: _p(
        'うまくいかないときは代わりの手段を答える',
        'Use the one in 〜 / Try 〜 instead',
        '壊れた時刻や置き場所だけでは代案にならない',
    ),
    16: _p(
        'Who 〜? には人（名前・関係）で答える',
        'My cousin / My teacher / A friend など',
        'いつ覚えたか・長さは人の答えではない',
    ),
    17: _p(
        'What if 〜? には代わりのやり方で答える',
        'Use 〜 instead / Try 〜',
        '道具の場所や過去の出来事だけでは「代わり」にならない',
    ),
    18: _p(
        'When will you rest / finish? には After / Before 〜',
        'After I 〜 / Before 〜 / When I finish 〜',
        '何のための作業か・起床の感想は「いつ休むか」ではない',
    ),
    19: _p(
        'What should we bring? には持ち物を答える',
        'A 〜 and some 〜 / Just in case, 〜',
        '場所の材質や季節の話は持ち物の答えではない',
    ),
    20: _p(
        'How is he / she now? にはいまの状態で答える',
        "He's fine. / She's OK. / He only needed 〜",
        '場所や昨日の忙しさは「いまどうか」ではない',
    ),
}

# --- Level 3 listening_conversation（会話：質問に答える）---
# 質問語の型 → 拾う情報。ひっかけ＝予備計画・もう一人の話・関連語だけ
L3_CONV: dict[int, Point] = {
    1: _p(
        'Where will they go? は本命の行き先を拾う',
        'pick it up / go to 〜 / meet at 〜 の場所',
        '閉まっていたときの予備日や集合時刻は本命の行き先ではない',
    ),
    2: _p(
        'When should 〜? は返す・やる期限を拾う',
        'before / by / until + 時刻・できごと',
        '早くやる理由やあとで使う時間は「いつ返すべきか」ではない',
    ),
    3: _p(
        'Why 〜? は Because + 本人が言った理由',
        'Because + 主語 + 動詞（なぜそうするか）',
        'クラブ名や「もし〜なら」の変更予定は、いまの理由ではない',
    ),
    4: _p(
        'What will 〜 do to help? は具体的な作業動詞',
        'I\'ll grate / carry / wash / cut 〜 など',
        '招待の話や手洗いなど準備だけでは「手伝いの中身」ではない',
    ),
    5: _p(
        'What still need to do? は still need / finish の残り',
        'I still need to finish 〜 / I haven\'t 〜 yet',
        'もう終わった部分や道具の申し出は「まだやること」ではない',
    ),
    6: _p(
        'How long has 〜? は Since / For で期間',
        'Since I was 〜 / For 〜 years',
        'レッスンの曜日や終了時点（Until）は期間の答えではない',
    ),
    7: _p(
        'What will they do if 〜? は if のときの予定',
        'If it rains / If 〜, we\'ll 〜 / We can 〜',
        '集合場所や晴れの日の予定は if の答えではない',
    ),
    8: _p(
        'Why say Don\'t worry? は安心材料の Because',
        'You\'ve practiced a lot. / You\'ll be fine if 〜',
        '追加のアドバイスと「心配しない理由」を取り違えない',
    ),
    9: _p(
        'How can 〜 get to 〜? は道順の動詞列',
        'Go past 〜 and turn right / left at 〜',
        '所要時間や開店時間だけでは行き方にならない',
    ),
    10: _p(
        'Do you mind if 〜? の許可は Not at all. など',
        'Not at all. / Of course not. / Go ahead.',
        '物の色や過去の動作は許可の返事ではない',
    ),
    11: _p(
        'Why bring 〜? は持っていく本人の Because',
        'Because + 必要な理由（道がない・使うから など）',
        'もう一人の持ち物や経験を、持っていく理由にしない',
    ),
    12: _p(
        'What must they do before 〜? は before / first の条件',
        'if we finish 〜 first / before 〜',
        '宿題をした場所や集合時刻を、事前にやることにすり替えない',
    ),
    13: _p(
        'How many times? は合計回数（Twice / Three times）',
        'I\'ve 〜 twice / three times.',
        '「1回は〜と」だけ拾って合計回数を減らさない',
    ),
    14: _p(
        'Why is 〜 heavy / 〜? は中身・原因の Because',
        'Because I brought / put 〜',
        'もう一人の経験や天気を、重さの理由にしない',
    ),
    15: _p(
        'Under what condition? / May I 〜? は If 〜 の条件',
        'Yes, if you 〜 afterward / Only if 〜',
        'もう一人が済ませた準備やメニュー名を条件にしない',
    ),
    16: _p(
        'How long has 〜 collected / 〜? は For / Since',
        'For about two years / Since I 〜',
        'もう一人が始めた時期を、本人の期間にしない',
    ),
    17: _p(
        'When can they borrow / 〜? は借りられる条件 If 〜',
        'If the room is empty / If no one is 〜',
        '先生に聞いたことや運ぶ時間を、借りられる条件にしない',
    ),
    18: _p(
        'Why bring / did you bring 〜? は用途の Because',
        'Because we\'ll paint / use / make 〜',
        'もう一人の準備や乾いたあとの作業を、持ってきた理由にしない',
    ),
    19: _p(
        'How many times has 〜 taken / 〜? は合計回数',
        'Three times. / Twice. など数字 + times',
        '一緒に行った人だけ拾って回数を変えたり、時刻表を回数にしない',
    ),
    20: _p(
        'When can they 〜? は Only if / If の許可条件',
        'Only if no one is 〜 / If 〜 is free',
        'いま見た場所や暗くなる前などの時刻を、条件そのものにしない',
    ),
}

# --- Level 3 listening_passage（英文：質問に答える）---
# 質問語の型 → 文中の対応表現。ひっかけ＝別の現在完了・すでに済んだこと・条件と理由の混同
L3_PASS: dict[int, Point] = {
    1: _p(
        'Where will 〜 work / go? は at / in + 場所',
        'work at 〜 / visit 〜 / go to 〜',
        '持ち帰りたいものやあとでしたいことは働く場所ではない',
    ),
    2: _p(
        'What did 〜 teach? は taught + how to 〜',
        'taught 〜 how to use / make / play 〜',
        'お礼の食事や練習の細部は「教えた内容」そのものではない',
    ),
    3: _p(
        'Why 〜 early / 〜? の目的は to + 動詞',
        'woke up early to 〜 / stayed to 〜',
        '他人が手伝ったことや別の用事を、本人の目的にしない',
    ),
    4: _p(
        'What does 〜 want to write about? は about の中身',
        'write a report about it → it が指すできごと・場所',
        '学ぶ細部（びんなど）だけをテーマ全体にすり替えない',
    ),
    5: _p(
        'What did 〜 do after 〜? は Then / after の次の行動',
        'Then he/she 過去形 〜',
        '練習時間など「前」の行動を after の答えにしない',
    ),
    6: _p(
        'How long has 〜 lived / 〜? は For / Since',
        'has lived 〜 for three years / since 〜',
        'したことがない経験や来年の予定は住んでいる期間ではない',
    ),
    7: _p(
        'How many times has 〜 before? は回数の数字',
        'twice before / three times / never',
        '今日の行き方や目的は「以前の回数」ではない',
    ),
    8: _p(
        'What still need to do? は残り・先生に言われたこと',
        'asked to add 〜 / still need to 〜',
        'すでに finish / print したことは「まだやること」ではない',
    ),
    9: _p(
        'What will 〜 do if 〜? は if 節のときの行動',
        'If it snows / rains, 〜 will 〜',
        'すでに買ってあるものやオンラインの希望は if の家族の予定ではない',
    ),
    10: _p(
        'How many times have they 〜? は数字 + times',
        'have cleaned / visited 〜 three times',
        '来週の予定や欠かしたことがない話はそうじの回数ではない',
    ),
    11: _p(
        'Why leave early / 〜? は because の直後',
        'leave early because 〜',
        'もう終わった宿題や席の話を早退の理由にしない',
    ),
    12: _p(
        'How many times this year / month? は期間つき回数',
        'four times this year / five times this month',
        '通う理由や借りた本の話は回数ではない',
    ),
    13: _p(
        'How long has 〜 checked / done 〜? は For + 期間',
        'for six months / for a year',
        'weeks と months の取り違えや、これから教える日を期間にしない',
    ),
    14: _p(
        'Why stay after school? は To 〜 / Because 〜 の目的',
        'stayed because she wanted to interview / to 〜',
        '以前の回数やあとからの発表を、残った理由にすり替えない',
    ),
    15: _p(
        'How many times this month? は今月の合計回数',
        'five times this month / already 〜 times',
        '明日の予定やふく理由を、今月の回数にしない',
    ),
    16: _p(
        'Why leave early? は because。If は別ルートの条件',
        'leaves early because the traffic is 〜',
        'ぬかるみで道を変える条件と、早出の理由を混ぜない',
    ),
    17: _p(
        'How long has 〜 studied 〜? は For + 期間',
        'for a year and a half / for two years',
        '手紙の通数や今週末の予定を期間の長さにしない',
    ),
    18: _p(
        'How many times this spring / season? は季節つき回数',
        'three times this spring',
        '入った理由や次の土曜の練習を、今春の回数にしない',
    ),
    19: _p(
        'Why skip / miss 〜? は because の約束・用事',
        'skip 〜 because he promised to 〜',
        '以前働いた回数やテレビの希望を、休む理由にしない',
    ),
    20: _p(
        'How long has 〜 lived in 〜? は For + 期間',
        'has lived 〜 for four years',
        '雨のときの廊下や毎朝の散歩は住んでいる期間ではない',
    ),
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
