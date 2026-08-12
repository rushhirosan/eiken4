#!/usr/bin/env python3
"""
英検3級 2026年度第1回を既存 data/questions/level3/*.txt に追記する。
既存問題は消さない（通し番号の続きから追加）。進捗は append_new_questions で維持。

公式 F 日程解答: https://www.eiken.or.jp/eiken/result/pdf/202601F3kyu.pdf
"""
from __future__ import annotations

from legacy_pdf_guard import require_legacy_pdf_tools_allowed

# 重い依存の import より先に止める（未インストール環境でもガードが効く）
if __name__ == "__main__":
    require_legacy_pdf_tools_allowed()

from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_Q = _REPO / 'data' / 'questions' / 'level3'

# 公式 F 日程解答（リーディング 1–30 / リスニング 1–30）
RW = {
    1: 3, 2: 3, 3: 1, 4: 2, 5: 2, 6: 1, 7: 4, 8: 4, 9: 2, 10: 2,
    11: 1, 12: 4, 13: 3, 14: 3, 15: 1,
    16: 2, 17: 3, 18: 4, 19: 2, 20: 4,
    21: 1, 22: 4, 23: 1, 24: 2, 25: 3,
    26: 1, 27: 2, 28: 4, 29: 3, 30: 2,
}
L = {
    1: 1, 2: 1, 3: 2, 4: 2, 5: 1, 6: 2, 7: 3, 8: 1, 9: 3, 10: 2,
    11: 2, 12: 3, 13: 3, 14: 3, 15: 1, 16: 4, 17: 3, 18: 3, 19: 1, 20: 1,
    21: 1, 22: 4, 23: 1, 24: 1, 25: 4, 26: 1, 27: 3, 28: 2, 29: 2, 30: 4,
}


def _choice_lines(choices: list[str]) -> str:
    return '\n'.join(f'{i}. {c}' for i, c in enumerate(choices, 1))


def _grammar_block(n: int, q: str, choices: list[str], ans: int, expl: str) -> str:
    return (
        f'問題{n}:\n{q}\n\n'
        f'選択肢{n}:\n{_choice_lines(choices)}\n\n'
        f'【正解{n}】\n{ans}. {choices[ans - 1]}\n\n'
        f'【解説{n}】\n{expl}\n'
    )


def grammar_blocks(start: int = 101) -> str:
    items = [
        (
            'A : What do you like to do on weekends, Bob?\n'
            'B: I like to ( ) at home. I often watch a movie.',
            ['move', 'plan', 'relax', 'grow'],
            '家で映画を見る、という流れなので「relax（くつろぐ）」が自然です。'
            '「move / plan / grow」では「家でくつろぐ」意味になりません。',
        ),
        (
            'A : Your shoes are so ( ), John.\n'
            'B: I know. I have to clean them.',
            ['clever', 'common', 'dirty', 'foolish'],
            '掃除が必要、と続くので「dirty（汚れている）」が自然です。'
            '「clever / common / foolish」は靴の汚れを表しません。',
        ),
        (
            'A : What happened to your leg, Bob?\n'
            'B: I had an ( ). I fell down the stairs this morning.',
            ['accident', 'advice', 'adult', 'addition'],
            '階段から落ちた、という話なので「accident（事故）」が自然です。'
            '「advice / adult / addition」はけがの原因として合いません。',
        ),
        (
            'A : What is that building?\n'
            'B: It’s the library. It’s a ( ) of our city.',
            ['sand', 'symbol', 'condition', 'bottle'],
            '街の象徴、という説明なので「symbol」が自然です。'
            '「sand / condition / bottle」は建物の役割を表しません。',
        ),
        (
            'Mr. Jones went to a nice restaurant with his family. He ( ) some cake for dessert.',
            ['arrived', 'ordered', 'taught', 'believed'],
            'デザートを頼む、なので「ordered（注文した）」が自然です。'
            '「arrived / taught / believed」ではケーキを頼む意味になりません。',
        ),
        (
            'The tomato soup that Mike made didn’t ( ) good. It was too salty.',
            ['taste', 'carry', 'find', 'serve'],
            '味がよくなかった、なので「taste」が自然です。'
            '「carry / find / serve」では「味がする」になりません。',
        ),
        (
            'A : It is a nice day today. Open the ( ), John.\n'
            'B: OK, Mom.',
            ['sentence', 'stadium', 'florist', 'curtain'],
            '開けて、と言っているので「curtain（カーテン）」が自然です。'
            '「sentence / stadium / florist」は開ける対象として不自然です。',
        ),
        (
            'I want a computer that is small ( ) to put in my backpack.',
            ['again', 'more', 'never', 'enough'],
            '「small enough to …（〜するのに十分小さい）」の決まりの形です。'
            '「again / more / never」ではこの構文になりません。',
        ),
        (
            'A : Why did you ( ) away your green sweater?\n'
            'B: It was really old.',
            ['fall', 'throw', 'hope', 'shop'],
            '古くて捨てた、なので「throw away（捨てる）」が自然です。'
            '「fall / hope / shop」では「捨てる」意味になりません。',
        ),
        (
            'On his way home from work, Jack gets ( ) the bus before his stop. '
            'He likes to walk for 30 minutes after sitting all day.',
            ['again', 'off', 'up', 'in'],
            'バス停より前で降りる、なので「get off（降りる）」が自然です。'
            '「again / up / in」では「バスを降りる」になりません。',
        ),
        (
            'A : Dad, can you give me a ( ) with my new TV? I need to bring it upstairs.\n'
            'B: Just a minute.',
            ['hand', 'face', 'leg', 'foot'],
            '「give me a hand（手伝って）」の決まり文句です。'
            '「face / leg / foot」では手伝いの依頼になりません。',
        ),
        (
            'Ethan lives far ( ) school, so he has to take the bus.',
            ['along', 'below', 'under', 'from'],
            '「far from（〜から遠い）」が自然です。'
            '「along / below / under」では距離の表現として合いません。',
        ),
        (
            'Jack finished ( ) his room and then went to his friend’s house.',
            ['clean', 'cleaned', 'cleaning', 'cleans'],
            'finish のあとは動名詞なので「cleaning」が正解です。'
            '「clean / cleaned / cleans」では finish の後ろの形として合いません。',
        ),
        (
            'Ken watched TV until twelve o’clock last night. His mother told him ( ) to bed earlier.',
            ['going', 'went', 'to go', 'goes'],
            'tell A to do の形なので「to go」が正解です。'
            '「going / went / goes」では tell のあとの不定詞になりません。',
        ),
        (
            'Ellen is good at ( ). Her friends enjoy going to her house and eating her delicious food.',
            ['cooking', 'to cook', 'cooked', 'cooks'],
            'be good at のあとは動名詞なので「cooking」が正解です。'
            '「to cook / cooked / cooks」では at の後ろの形として合いません。',
        ),
    ]
    parts = []
    for i, (q, choices, expl) in enumerate(items):
        n = start + i
        ans = RW[i + 1]
        parts.append(_grammar_block(n, q, choices, ans, expl))
    return '\n---\n\n'.join(parts)


def conversation_blocks(start: int = 51) -> str:
    items = [
        (
            'Boy : I’m planning to go to Paris this summer. ( )\n'
            'Girl : Yes, it’s a very beautiful place.',
            [
                'Would you like some?',
                'Have you ever been there?',
                'Did you find your bag?',
                'How much are the tickets?',
            ],
            '相手が「はい、とても美しい場所です」と返すので、'
            '行ったことがあるかを聞く「Have you ever been there?」が自然です。'
            '食べ物・かばん・値段の話ではこの返事と合いません。',
        ),
        (
            'Man : Why don’t we play tennis together on Saturday?\n'
            'Woman : ( ) I was thinking the same thing.',
            [
                'Have a nice time.',
                'It’ll be here soon.',
                'That sounds great.',
                'I can’t understand.',
            ],
            '同じことを考えていた、と続くので賛成の「That sounds great.」が自然です。'
            'あいさつ・到着・理解できない、では提案への同意になりません。',
        ),
        (
            'Mother : Samantha, dinner is ready. Come downstairs.\n'
            'Daughter : OK, Mom. ( )',
            [
                'I’m too busy.',
                'I’ll call you soon.',
                'I’m going tomorrow.',
                'I’ll be there in a minute.',
            ],
            '呼ばれて「わかった」と答えたあとなので、'
            '「I’ll be there in a minute.（すぐ行くよ）」が自然です。'
            '忙しい・後で電話・明日行く、では今すぐ下りる流れと合いません。',
        ),
        (
            'Wife : You’re not eating your breakfast. ( )\n'
            'Husband : I’m just not hungry.',
            [
                'Are they your friends?',
                'What’s the matter?',
                'Can you do it alone?',
                'Do you have any?',
            ],
            '朝食を食べていない理由を尋ねる「What’s the matter?」が自然です。'
            '友人・一人でできるか・持っているか、ではこの返事とつながりません。',
        ),
        (
            'Man 1 : Excuse me. I think you’re wearing my jacket.\n'
            'Man 2 : Oh, ( ) It looks like mine.',
            [
                'it’s my pleasure.',
                'I decided to go.',
                'I’ll speak to him now.',
                'I’m very sorry.',
            ],
            '間違えて着ていたことへの「I’m very sorry.（すみません）」が自然です。'
            'どういたしまして・行くと決めた・彼に話す、では謝罪になりません。',
        ),
    ]
    parts = []
    for i, (q, choices, expl) in enumerate(items):
        n = start + i
        ans = RW[16 + i]
        parts.append(_grammar_block(n, q, choices, ans, expl))
    return '\n---\n\n'.join(parts)


def reading_blocks(start_passage: int = 16) -> str:
    p16 = start_passage
    p17 = start_passage + 1
    p18 = start_passage + 2
    a_text = (
        "Mr. Chen's Cooking Classes\n\n"
        'Are you interested in traditional Chinese dishes?\n'
        'Next March, Evansfield Cultural Center will hold cooking classes for '
        'people who want to learn about Chinese recipes. We will invite '
        'Mr. Chen as a special teacher.\n\n'
        '●Remember to bring an apron and a notebook.\n\n'
        'Place\n'
        'Evansfield Cultural Center\n'
        'Classes\n'
        '(For adults) Fridays, 7:00 p.m. to 9:00 p.m.\n'
        '(For teenagers) Saturdays, 2:00 p.m. to 3:30 p.m.\n'
        'About the teacher\n'
        'Mr. Chen is one of the best chefs in our city. He has won some '
        'international cooking contests. He was also chosen as Great Young Chef '
        'of the Year last year.'
    )
    a_qs = [
        (
            'What should the members of the classes do?',
            [
                'Bring a notebook.',
                'Wash the dishes after cooking.',
                'Buy Mr. Chen’s recipe book.',
                'Learn to speak Chinese.',
            ],
            1,
            '掲示に「Remember to bring an apron and a notebook」とあるので、'
            'ノートを持参する 1 が正解です。皿洗い・レシピ本購入・中国語学習の指示はありません。',
        ),
        (
            'Mr. Chen is a chef who',
            [
                'gave lessons to students online.',
                'taught teenagers on Saturday mornings.',
                'invited his friends to the cooking classes.',
                'won some cooking contests.',
            ],
            4,
            '「He has won some international cooking contests」とあるので 4 が正解です。'
            'オンライン授業・土曜朝・友人招待の記述はありません。',
        ),
    ]
    b_text = (
        'From: Judy Smith\n'
        'To: Ann Smith\n'
        'Date: December 8\n'
        'Subject: Winter sale\n\n'
        'Dear Grandma,\n'
        'Thank you for giving me a lovely present last month. I really like the wallet!\n'
        'Yesterday, I visited a department store near the station. They were having a '
        'winter sale! You said you wanted a brown sweater, right? I looked for one, '
        'but I couldn’t find any brown ones. However, I saw a nice scarf and bought '
        'it for you! I also bought a coat for myself. Can I bring the scarf to you?\n'
        'Will you be home this Saturday?\n'
        'Write back soon,\n'
        'Judy\n\n'
        '-\n\n'
        'From: Ann Smith\n'
        'To: Judy Smith\n'
        'Date: December 8\n'
        'Subject: Thank you!\n\n'
        'Dear Judy,\n'
        'I am glad to hear that you like the wallet. I found it at a shopping mall '
        'next to the museum. Thank you for the scarf! Yes, I will be home this '
        'Saturday, and my old friend Linda will also visit my house that day! I have '
        'not seen her since she moved to another city two years ago. Do you '
        'remember her? You often met her at my house when you were little. You '
        'can see her this Saturday if you come here. By the way, will your mom '
        'come with you that day?\n'
        'Love,\n'
        'Grandma\n\n'
        '-\n\n'
        'From: Judy Smith\n'
        'To: Ann Smith\n'
        'Date: December 8\n'
        'Subject: Great!\n\n'
        'Dear Grandma,\n'
        'Yes, I remember Linda! She was very kind to me! Linda often told me '
        'stories when you were cooking in the kitchen. They were so interesting! I '
        'want to meet her, too! But my mom cannot come with me that day because '
        'she has to work. I will visit you alone by bus. Yesterday, I also found a '
        'new cake shop near the park, so I will buy some cakes for you and Linda '
        'before I visit your house.\n'
        'See you soon,\n'
        'Judy'
    )
    b_qs = [
        (
            'What did Judy do at the department store yesterday?',
            [
                'She bought a coat and a scarf.',
                'She found a nice wallet.',
                'She bought a brown sweater.',
                'She worked as a staff member.',
            ],
            1,
            '茶色のセーターは見つからず、スカーフを祖母用に、コートを自分用に買った、とあるので 1 が正解です。'
            '財布は祖母からのプレゼントで、店員として働いた記述はありません。',
        ),
        (
            'Judy’s grandmother bought the wallet',
            [
                'at a shop in the park.',
                'at a shopping mall beside the museum.',
                'at a shop next to her house.',
                'at a department store in Linda’s city.',
            ],
            2,
            '祖母のメールに「I found it at a shopping mall next to the museum」とあるので 2 が正解です。',
        ),
        (
            'What did Judy often do when her grandmother was cooking?',
            [
                'She shared a cake with Linda.',
                'She visited a park with her mother.',
                'She listened to Linda’s stories.',
                'She helped her grandmother in the kitchen.',
            ],
            3,
            '「Linda often told me stories when you were cooking」とあるので、'
            '料理中にリンダの話を聞いていた 3 が正解です。',
        ),
    ]
    c_text = (
        'Never Too Late\n\n'
        'Anna Mary Robertson Moses, also known as Grandma Moses, '
        'was an American artist. She was born in 1860 on a farm in New '
        'York. As a girl, Anna worked hard on the farm and took care of '
        'her family. She liked to play outside with her brothers in her free '
        'time. She also loved making things with her hands. She '
        'often enjoyed drawing pictures on paper her father bought for her.\n\n'
        'Anna married Thomas Moses in 1887 and lived on the local '
        'farm she loved. Even after Thomas died in 1927, she kept working '
        'on her farm with the help of her youngest son. But when she got '
        'older, it was hard for her to do some things on the farm because '
        'her hands hurt. So, she decided to try painting instead. She was '
        'already over seventy-five years old then.\n\n'
        'Anna painted all the things she loved from her farm life. She '
        'often painted green fields, snowy winters, and happy people living '
        'in nature. Her paintings were so unique and full of happiness that '
        'a lot of people wanted to see them. They felt so warm and happy '
        'when they saw her works painted in a simple way with many '
        'colors.\n\n'
        'Anna kept painting until about 1960. She created more than '
        '1,500 works of art in her life, and her paintings became popular '
        'across the country. Even today, many people come to see '
        'her paintings in museums. Anna and her paintings show that anyone '
        'can try something new at any time in their life.'
    )
    c_qs = [
        (
            'What did Anna like when she was a child?',
            [
                'Drawing on paper.',
                'Taking pictures.',
                'Buying gifts for her father.',
                'Playing games at home.',
            ],
            1,
            '「enjoyed drawing pictures on paper」とあるので 1 が正解です。'
            '写真・贈り物・室内ゲームの記述はありません。',
        ),
        (
            'Why did Anna begin painting?',
            [
                'She had to teach art to her son.',
                'She had a problem with her hands.',
                'She did not want to look old.',
                'She did not enjoy living on her farm.',
            ],
            2,
            '手が痛くて農作業が難しくなり絵を始めた、とあるので 2 が正解です。',
        ),
        (
            'The paintings Anna created',
            [
                'made her much poorer.',
                'made people free.',
                'were sold to farmers.',
                'had a lot of colors.',
            ],
            4,
            '「painted in a simple way with many colors」とあるので 4 が正解です。',
        ),
        (
            'What did Anna do in her life?',
            [
                'She tried to travel across America.',
                'She invented new colors.',
                'She created many works of art.',
                'She built a famous museum.',
            ],
            3,
            '「created more than 1,500 works of art」とあるので 3 が正解です。',
        ),
        (
            'What is this story about?',
            [
                'A woman who loved her grandmother.',
                'A popular artist in America.',
                'How to live on a farm.',
                'How to help older people.',
            ],
            2,
            'アメリカの人気画家 Grandma Moses の生涯が主題なので 2 が正解です。'
            '祖母を愛する話・農場の暮らし方・高齢者支援のハウツーではありません。',
        ),
    ]

    def fmt_passage(num: int, body: str, qs: list) -> str:
        letters = 'abcdefghij'
        chunks = [f'本文{num}\n{body}\n']
        for i, (qt, choices, ans, expl) in enumerate(qs):
            lab = f'{num}{letters[i]}'
            chunks.append(
                f'問題{lab}:\n{qt}\n\n'
                f'選択肢{lab}:\n{_choice_lines(choices)}\n\n'
                f'【正解{lab}】\n{ans}. {choices[ans - 1]}\n\n'
                f'【解説{lab}】\n{expl}\n'
            )
        return '\n'.join(chunks)

    return '\n---\n\n'.join(
        [
            fmt_passage(p16, a_text, a_qs),
            fmt_passage(p17, b_text, b_qs),
            fmt_passage(p18, c_text, c_qs),
        ]
    )


def writing_blocks(start: int = 21) -> str:
    email = f'''問題{start}:
友人 James から次のメールをもらいました。読んで英文で返信メールを書きなさい。James の 2 つの質問（下線部）に答えること。

●あなたが書く返信メールのうち、James に対応する英文の語数の目安は 15～25 語です。
●解答は以下のテキストボックスに書きなさい。
●解答が James のメールに対応していないと判断された場合は 0 点と採点されることがあります。James のメールの内容をよく読んでから答えてください。
●空行の下の Best wishes, の後にあなたの名前を書く必要はありません。

Hi,
Thank you for your e-mail.
I heard that you came back from India yesterday. I have some questions for you. <u>What did you do during your flight from India?</u> <u>And what time did you return to your house yesterday?</u>
Your friend,
James

Hi, James!
Thank you for your e-mail.



Best wishes,

【参考解答】
■ この問題で求められること
James からのメールに対して、下線部の2つの質問（飛行機の中で何をしたか／昨日何時に家に帰ったか）に、それぞれ英文で答えます。

■ 書き方のポイント
・2つの質問に必ず答える（どちらかだけだと不十分になりやすいです）。
・James に向けた本文は語数の目安 15～25 語。
・What did you do...? には過去形で行動を答え、what time...? には時刻を答えます。

■ 参考解答の例
I watched some movies during my flight from India. I returned home at ten o’clock last night. I had a good time on the flight.

■ 表現のメモ
飛行機内の行動：watched movies / read a book / slept。
帰宅時刻：at ten o’clock / at around 9 p.m. など。
'''
    essay = f'''問題{start + 1}:
次の QUESTION について、あなたの考えとその理由を 2 つの英文で書きなさい。語数の目安は 25～35語。
●文数の目安はピリオド（.）で数えると3〜4個になることもあります。2つの英文＝意見1文＋理由1文の型を目指しましょう。

QUESTION
Do you like to get up early in winter?

【参考解答】
■ この問題で求められること
QUESTION に対して、あなたの意見（冬の早起きが好きかどうか）と、その理由を英文で書きます。理由は2つ入れるのが基本です。

■ 書き方のポイント
・1文目：Yes, I do. / No, I don’t. ではっきり答える。
・続けて I have two reasons. First, ... Second, ... で理由を2つ書く。
・語数の目安は 25～35 語。理由は具体的に（静かな朝、公園が気持ちよい、など）。

■ 参考解答の例
Yes, I do. I have two reasons. First, I can study better on quiet early mornings in winter. Second, I feel good when I spend time in the park on sunny winter mornings.

■ 別の書き方の例（好きではない場合）
No, I don’t. I have two reasons. First, it is still dark and cold in the morning. Second, I want to sleep longer on winter mornings.
'''
    return email.strip() + '\n\n---\n\n' + essay.strip() + '\n'


def listening_illustration_blocks(start: int = 41) -> str:
    # 原稿の ★/☆ を M/W 表記に揃えつつ、選択肢は公式冊子どおり
    items = [
        (
            'M: What is a popular book for young children?\n'
            'W: Here is a good one.\n'
            'M: What kind of book is it?',
            ['It’s science fiction.', 'I read it at school.', 'They like animals.'],
            '本の種類を聞いているので、1「It’s science fiction.（SFです。）」が自然です。'
            '2はいつ読んだか、3は好きなものの話で、種類の答えになりません。',
        ),
        (
            'M: Do you still have my history textbook?\n'
            'W: Yes, Scott.\n'
            'M: Well, I’ll need it next week.',
            ['I can bring it tomorrow.', 'I hope you can buy it.', 'I’ll take a look.'],
            '来週必要、と言っているので、返す約束の1「I can bring it tomorrow.」が自然です。'
            '買ってほしい・探してみる、では「持っている」前提の流れに合いにくいです。',
        ),
        (
            'M: You need to clean your room, Jane.\n'
            'W: I’ll do it tomorrow.\n'
            'M: Why can’t you do it today?',
            ['It’s in the living room.', 'I have to study for a test.', 'Thanks for helping me.'],
            '今日できない理由を聞いているので、2「I have to study for a test.」が自然です。'
            '場所やお礼では理由の答えになりません。',
        ),
        (
            'M: Here’s your steak. Would you like anything else?\n'
            'W: No, thanks.\n'
            'M: OK. Enjoy your meal.',
            ['Yes, that’s fine.', 'I’m sure I will.', 'Just one, please.'],
            '「楽しんで」への返事なので、2「I’m sure I will.（きっとそうするよ。）」が自然です。'
            '1や3はこの締めのあいさつへの応答として弱くなります。',
        ),
        (
            'M: When are you going on vacation, Marge?\n'
            'W: In two weeks.\n'
            'M: Where will you go?',
            ['To a beach in Thailand.', 'Two or three of them, please.', 'To my Spanish class.'],
            '行き先を聞いているので、1「To a beach in Thailand.」が自然です。'
            '個数やクラスの話は場所の答えになりません。',
        ),
        (
            'W: What’s your favorite subject?\n'
            'M: I love studying English.\n'
            'W: How often do you study?',
            ['After two months.', 'For one hour every afternoon.', 'I went to America last year.'],
            '頻度を聞いているので、2「For one hour every afternoon.」が自然です。'
            '「〜のあと」や過去の渡航は頻度の答えになりません。',
        ),
        (
            'M: Excuse me. Does this train stop at Green Hills?\n'
            'W: Yes. I get off there, too.\n'
            'M: That’s good to know. Thanks.',
            ['I don’t take a train.', 'It’s big.', 'It’s my pleasure.'],
            'お礼への定番の返事は、3「It’s my pleasure.（どういたしまして。）」です。'
            '電車に乗らない・大きい、はこのやりとりに合いません。',
        ),
        (
            'M: Has Naomi found her book?\n'
            'W: No, she still hasn’t.\n'
            'M: Did she check the classroom?',
            ['She couldn’t find it there.', 'It was in her bag.', 'The teacher gave it to her.'],
            '教室を調べたかへの答えなので、見つからなかった1が自然です。'
            '2や3は「まだ見つかっていない」という直前の話と矛盾しやすいです。',
        ),
        (
            'W: Tom, your shoes are old.\n'
            'M: I know. I’ve used them for two years.\n'
            'W: I can even see a hole.',
            ['You went to the department store.', 'Your socks are very pretty.', 'Oh, I’ll get new ones.'],
            '穴が空いている、と言われたあとの反応なので、3「新しいのを買う」が自然です。'
            'デパートに行った・靴下のほめ言葉では穴への応答になりません。',
        ),
        (
            'M: I want to go to the library.\n'
            'W: It’s going to rain soon.\n'
            'M: But I wanted to ride my bike there.',
            ['Wait until it stops snowing.', 'That’s not a good idea.', 'I went for a walk.'],
            '雨なのに自転車で行こうとしているので、2「That’s not a good idea.」が自然です。'
            '雪の話や散歩した話は、この助言としてずれます。',
        ),
    ]
    parts = []
    for i, (dialog, choices, expl) in enumerate(items):
        n = start + i
        ans = L[i + 1]
        parts.append(
            f'No.{n}:\n{dialog}\n\n'
            f'Question No.{n}:\n{_choice_lines(choices)}\n\n'
            f'【正解{n}】\n{ans}. {choices[ans - 1]}\n\n'
            f'【解説{n}】\n放送文\n{dialog}\n\n{expl}\n'
        )
    return '\n---\n\n'.join(parts)


def listening_conversation_blocks(start: int = 41) -> str:
    items = [
        (
            'M: Did you join the art club again this year, Kathy?\n'
            'W: No. I wanted to try something new, so I joined the dance club.\n'
            'M: I joined the swimming club.\n'
            'W: Sounds like fun.',
            'What club is Kathy in this year?',
            [
                'The art club.',
                'The dance club.',
                'The music club.',
                'The swimming club.',
            ],
            'Kathy は dance club に入った、と明言しているので 2 が正解です。'
            'art は今年はやめており、swimming は相手のクラブです。',
        ),
        (
            'M: I don’t want to go to the park. It’s too hot.\n'
            'W: But Sam, we planned to have a picnic!\n'
            'M: I’m sorry, but I hate this kind of weather.\n'
            'W: OK, let’s stay home.',
            'Why did they decide to stay home?',
            [
                'Sam doesn’t like the park.',
                'Sam doesn’t like picnics.',
                'Sam doesn’t like hot days.',
                'Sam doesn’t like rainy days.',
            ],
            '暑いのが嫌だ、と言って家にいることにしたので 3 が正解です。'
            '公園やピクニック自体が嫌い、雨の日の話ではありません。',
        ),
        (
            'M: Hey, Jane, let’s go and get something to eat.\n'
            'W: OK, Bob. Let’s go to the Chinese restaurant on 5th Street. It’s very popular.\n'
            'M: Sounds good, but isn’t it expensive?\n'
            'W: A little, but the food is really good.',
            'What does Jane think of the Chinese restaurant?',
            [
                'It isn’t popular.',
                'It isn’t expensive.',
                'The food is good.',
                'The restaurant is small.',
            ],
            '「the food is really good」と言っているので 3 が正解です。'
            '人気はある、少し高い、小ささの話はありません。',
        ),
        (
            'M: Let’s go shopping on Saturday afternoon, Betty.\n'
            'W: I’d love to, but I have to work.\n'
            'M: How about Sunday before lunch, then?\n'
            'W: Sure. Let’s meet at the station at ten.',
            'When will they meet?',
            [
                'Saturday morning.',
                'Saturday afternoon.',
                'Sunday morning.',
                'Sunday afternoon.',
            ],
            '日曜の昼食前・駅で10時、なので 3「Sunday morning」が正解です。'
            '土曜午後は仕事で行けません。',
        ),
        (
            'M: Where were you this morning? We had a science club meeting.\n'
            'W: Really?\n'
            'M: Yes. Mr. Burns told us about it yesterday.\n'
            'W: I wasn’t at school yesterday.',
            'What happened to the girl this morning?',
            [
                'She missed a meeting.',
                'She couldn’t find Mr. Burns.',
                'She lost her science report.',
                'She was late for a test.',
            ],
            '今朝の科学クラブの会合にいなかった、ので 1 が正解です。',
        ),
        (
            'W: Ken, why aren’t you at school?\n'
            'M: Sorry, Mom. I woke up late this morning.\n'
            'W: I am very angry. Please go after breakfast.\n'
            'M: OK.',
            'Why is Ken’s mother angry?',
            [
                'Ken did not make breakfast.',
                'Ken did not come home early.',
                'Ken has not cleaned his room.',
                'Ken has not left for school.',
            ],
            'まだ学校へ行っていない（起き遅れた）ことに怒っているので 4 が正解です。',
        ),
        (
            'W: I’m reading a book about science.\n'
            'M: That sounds interesting. I want to read about history.\n'
            'W: You should read this mystery book.\n'
            'M: OK, I’ll borrow that instead.',
            'Which book will the boy borrow?',
            [
                'A history book.',
                'A math book.',
                'A mystery book.',
                'A science book.',
            ],
            '代わりに mystery book を借りる、と言っているので 3 が正解です。'
            'history は読みたいと思っていただけです。',
        ),
        (
            'W: Tom, do you want to play soccer after school?\n'
            'M: Sorry, I can’t. I’m going to the park with my cousin.\n'
            'W: Oh, I see. Well, have fun.\n'
            'M: Thanks.',
            'Who is Tom going to the park with?',
            ['His friend.', 'His parents.', 'His cousin.', 'His sister.'],
            '「with my cousin」とあるので 3 が正解です。',
        ),
        (
            'M: Is this blue book yours, Sarah?\n'
            'W: No, mine has a green cover. I think it is Ken’s.\n'
            'M: No, his book is yellow.\n'
            'W: Then, it is probably Emily’s. Let’s ask her later.',
            'Which book is Sarah’s?',
            [
                'The one with a green cover.',
                'The one with a red cover.',
                'The one with a blue cover.',
                'The one with a yellow cover.',
            ],
            'Sarah の本は green cover、と本人が言っているので 1 が正解です。'
            '青い本は今見ている本、黄色は Ken の本です。',
        ),
        (
            'W: What do you like to do in your free time, Mark?\n'
            'M: I love painting. How about you?\n'
            'W: I play the guitar and write songs.\n'
            'M: That’s cool.',
            'What does Mark do in his free time?',
            [
                'He paints.',
                'He writes songs.',
                'He plays the guitar.',
                'He sings.',
            ],
            'Mark は painting が好き、と言っているので 1 が正解です。'
            'ギターや作曲は相手の趣味です。',
        ),
    ]
    parts = []
    for i, (dialog, q, choices, tip) in enumerate(items):
        n = start + i
        ans = L[11 + i]
        parts.append(
            f'No.{n}:\n{dialog}\n\n'
            f'Question No.{n}:\n{q}\n\n'
            f'{_choice_lines(choices)}\n\n'
            f'【正解{n}】\n{ans}. {choices[ans - 1]}\n\n'
            f'【解説{n}】\n放送文\n{dialog}\n\n'
            f'Question: {q}\n\n{tip}\n'
        )
    return '\n---\n\n'.join(parts)


def listening_passage_blocks(start: int = 41) -> str:
    items = [
        (
            'W: My mom is an elementary school teacher, and my dad teaches science at a high school. '
            'My friends think I’ll become a teacher, too, but I want to be a famous violinist.',
            'What does the girl want to be?',
            [
                'A famous musician.',
                'A high school teacher.',
                'An elementary school teacher.',
                'A scientist.',
            ],
            '有名なバイオリニストになりたい、なので 1「A famous musician」が正解です。'
            '教師は親の職業・友人の予想です。',
        ),
        (
            'M: Amy works five days a week, but next year, she’ll only work three. '
            'She wants to spend more time with her son. He’s only two years old.',
            'How many days a week does Amy work now?',
            ['One.', 'Two.', 'Three.', 'Five.'],
            '今は週5日、来年は週3日、なので 4「Five」が正解です。Three は来年の予定です。',
        ),
        (
            'M: Rick wants money to buy a new bike. He wanted to work at his favorite restaurant, '
            'but the restaurant didn’t need any help. So he got a job at a supermarket. '
            'He’ll start next week.',
            'How will Rick get money to buy a bike?',
            [
                'He’ll work at a supermarket.',
                'He’ll ask his parents.',
                'He’ll work at a restaurant.',
                'He’ll ask his grandparents.',
            ],
            'スーパーで働くことになった、ので 1 が正解です。レストランは採用されませんでした。',
        ),
        (
            'M: Mark wasn’t feeling well in school today and wanted to go home. '
            'His teacher called Mark’s mother. Mark’s mother came to school and took him to the doctor.',
            'What did Mark’s teacher do?',
            [
                'She called Mark’s mother.',
                'She took Mark home.',
                'She took Mark to the doctor.',
                'She gave Mark some medicine.',
            ],
            '先生がしたのは母親に電話することなので 1 が正解です。'
            '家や病院へ連れて行ったのは母親です。',
        ),
        (
            'W: I’m going to an important event, so I need some nice clothes. '
            'I already have nice shoes, but I need to get a new skirt. '
            'I’ll also wear the watch my brother gave me.',
            'What will the woman buy for the event?',
            ['Gloves.', 'Shoes.', 'A watch.', 'A skirt.'],
            '新しく買う必要があるのはスカート、なので 4 が正解です。'
            '靴はすでにあり、時計は兄からもらったものです。',
        ),
        (
            'M: I usually make breakfast for my family. Today, I got up late, so my father made breakfast. '
            'He made pancakes for my brother and me. They were delicious.',
            'Who made breakfast today?',
            [
                'The boy’s father.',
                'The boy’s mother.',
                'The boy’s brother.',
                'The boy.',
            ],
            '今日は父親が作った、ので 1 が正解です。普段作るのは少年本人です。',
        ),
        (
            'W: My brother is a college student. He gets up at seven, eats breakfast for half an hour, '
            'and leaves home at eight. He starts his classes at nine and studies until six.',
            'What time does the woman’s brother leave home?',
            ['At 7:00.', 'At 7:30.', 'At 8:00.', 'At 9:00.'],
            '家を出るのは eight、なので 3 が正解です。7時は起床、9時は授業開始です。',
        ),
        (
            'W: Thank you for coming to our restaurant. Today’s special is chicken curry. '
            'It comes with fresh bread. The cook is making it in the kitchen now. Enjoy your meal.',
            'Where is the woman talking?',
            [
                'In a supermarket.',
                'In a restaurant.',
                'In a library.',
                'In a train station.',
            ],
            'レストランへの来店にお礼を言っているので 2 が正解です。',
        ),
        (
            'M: John went to the supermarket yesterday. He wanted to buy some chocolate, '
            'but the supermarket did not have any. He bought some apples and a bottle of orange juice instead.',
            'What did John want to buy?',
            [
                'Some apples.',
                'Some chocolate.',
                'Some oranges.',
                'Some juice.',
            ],
            '買いたかったのはチョコレート、なので 2 が正解です。りんごやジュースは代わりに買ったものです。',
        ),
        (
            'W: There was a big festival in my town last weekend. I went with my sister, '
            'and I met some of my friends there. I was happy to see them.',
            'Where did the woman go last weekend?',
            [
                'To her sister’s house.',
                'To a museum.',
                'To her friend’s house.',
                'To a festival.',
            ],
            '町の大きなフェスティバルに行った、ので 4 が正解です。'
            '妹は同行者、友人はそこで会った相手です。',
        ),
    ]
    parts = []
    for i, (passage, q, choices, tip) in enumerate(items):
        n = start + i
        ans = L[21 + i]
        parts.append(
            f'No.{n}:\n{passage}\n\n'
            f'Question No.{n}:\n{q}\n\n'
            f'{_choice_lines(choices)}\n\n'
            f'【正解{n}】\n{ans}. {choices[ans - 1]}\n\n'
            f'【解説{n}】\n放送文\n{passage}\n\n'
            f'Question: {q}\n\n{tip}\n'
        )
    return '\n---\n\n'.join(parts)


def _append(path: Path, block: str) -> None:
    text = path.read_text(encoding='utf-8').rstrip() + '\n\n---\n\n' + block.strip() + '\n'
    path.write_text(text, encoding='utf-8')
    print(f'appended -> {path}')


def main() -> None:
    require_legacy_pdf_tools_allowed()
    _append(_Q / 'grammar_fill_questions.txt', grammar_blocks(101))
    _append(_Q / 'conversation_questions.txt', conversation_blocks(51))
    _append(_Q / 'reading_comprehesion_questions.txt', reading_blocks(16))
    _append(_Q / 'writing_questions.txt', writing_blocks(21))
    _append(_Q / 'listening_illustration_questions.txt', listening_illustration_blocks(41))
    _append(_Q / 'listening_conversation_questions.txt', listening_conversation_blocks(41))
    _append(_Q / 'listening_passage_questions.txt', listening_passage_blocks(41))
    print('done')


if __name__ == '__main__':
    main()
