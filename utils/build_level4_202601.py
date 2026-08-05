#!/usr/bin/env python3
"""
英検4級 2026年度第1回を既存 data/questions/*.txt に追記する。
既存問題は消さない（通し番号の続きから追加）。
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_Q = _REPO / 'data' / 'questions'

# 公式 F 日程解答
RW = {
    1: 2, 2: 3, 3: 1, 4: 1, 5: 3, 6: 2, 7: 1, 8: 2, 9: 2, 10: 1,
    11: 1, 12: 1, 13: 4, 14: 2, 15: 3,
    16: 4, 17: 2, 18: 4, 19: 3, 20: 3,
    21: 2, 22: 1, 23: 2, 24: 3, 25: 3,
    26: 1, 27: 2, 28: 3, 29: 3, 30: 1,
    31: 3, 32: 3, 33: 4, 34: 1, 35: 3,
}
L = {
    1: 1, 2: 3, 3: 2, 4: 1, 5: 1, 6: 1, 7: 3, 8: 1, 9: 3, 10: 2,
    11: 1, 12: 2, 13: 3, 14: 4, 15: 4, 16: 3, 17: 4, 18: 3, 19: 4, 20: 1,
    21: 2, 22: 3, 23: 3, 24: 4, 25: 2, 26: 4, 27: 1, 28: 3, 29: 1, 30: 4,
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


def _conv_block(n: int, q: str, choices: list[str], ans: int, expl: str) -> str:
    return _grammar_block(n, q, choices, ans, expl)


def grammar_blocks(start: int = 166) -> str:
    items = [
        (
            'A : I want to make some pancakes for breakfast, but we don’t have any ( ).\n'
            'B : I’ll go to the store and get some.',
            ['flowers', 'eggs', 'books', 'sports'],
            'パンケーキを作るのに足りないのは「eggs（卵）」が自然です。'
            '「flowers / books / sports」は材料になりません。',
        ),
        (
            'A : I want to call my mother, but I don’t have a phone.\n'
            'B : You can ( ) my phone.',
            ['climb', 'leave', 'use', 'send'],
            '電話を貸す流れなので「use（使う）」が自然です。'
            '「climb / leave / send」では「私の電話を〜」の意味が合いません。',
        ),
        (
            'A : Mom, I want to make some cookies.\n'
            'B : All right, but please ( ) this carrot first.',
            ['cut', 'arrive', 'hit', 'run'],
            'にんじんを先に処理する流れなので「cut（切る）」が自然です。'
            '「arrive / hit / run」はこの文脈に合いません。',
        ),
        (
            'A : Is it warm in your ( ) now?\n'
            'B : Yes, it’s spring.',
            ['country', 'ticket', 'animal', 'road'],
            '春で暖かい、という国・土地の話なので「country」が自然です。'
            '「ticket / animal / road」は暖かさの場所として不自然です。',
        ),
        (
            'Taro enjoyed the chorus ( ) on TV yesterday. He wants to join a chorus at school.',
            ['wall', 'hobby', 'contest', 'trip'],
            'テレビの合唱コンクールを楽しんだ、という流れなので「contest」が自然です。'
            '「wall / hobby / trip」では意味が合いません。',
        ),
        (
            'A : Can I study in the library today?\n'
            'B : Yes, it’s ( ) now.',
            ['cold', 'open', 'late', 'favorite'],
            '今使える・空いている、という返事なので「open」が自然です。'
            '「cold / late / favorite」では図書館の利用可否になりません。',
        ),
        (
            'Sally went to eat Chinese food in a big ( ) last weekend.',
            ['city', 'word', 'body', 'point'],
            '大きな街で中華を食べた、という文なので「city」が自然です。'
            '「word / body / point」は場所になりません。',
        ),
        (
            'A : What do you want to do tomorrow afternoon?\n'
            'B : I have an ( ). Let’s go to the aquarium.',
            ['end', 'idea', 'arm', 'eraser'],
            '提案の前置きなので「idea（考え）」が自然です。'
            '「end / arm / eraser」はこの会話に合いません。',
        ),
        (
            'A : These are my new glasses. What do you ( ) of them?\n'
            'B : They’re really nice, Grandma.',
            ['watch', 'think', 'tell', 'finish'],
            '「What do you think of …?（〜をどう思う？）」の決まり文句です。'
            '「watch / tell / finish」ではこの形になりません。',
        ),
        (
            'A : Mom, I’m going to play in the soccer game tomorrow.\n'
            'B : Good ( ) you. You practiced a lot.',
            ['for', 'with', 'in', 'after'],
            '「Good for you.（よかったね／えらいね）」が自然です。'
            '「with / in / after」では決まり文句になりません。',
        ),
        (
            'A : Did you ( ) about Dan?\n'
            'B : Yes. He’s going to move back to England.',
            ['hear', 'wait', 'run', 'want'],
            '知らせを聞いたか、なので「hear」が自然です。'
            '「wait / run / want」では「〜について聞いた」になりません。',
        ),
        (
            'A : Here are four cookies, Bob. Please ( ) them with your sister.\n'
            'B : OK. I’ll give her two of them.',
            ['share', 'answer', 'cry', 'run'],
            '妹と分けるので「share」が自然です。'
            '「answer / cry / run」は分け与える意味になりません。',
        ),
        (
            'A : Today, apples are ( ) than bananas.\n'
            'B : OK. Let’s get some apples.',
            ['cheap', 'cheapest', 'the cheapest', 'cheaper'],
            'than があるので比較級「cheaper」が必要です。'
            '「cheap / cheapest / the cheapest」では than と合いません。',
        ),
        (
            'The students ( ) 50 meters in the school pool yesterday.',
            ['swim', 'swam', 'swimming', 'to swim'],
            'yesterday があるので過去形「swam」が自然です。'
            '「swim / swimming / to swim」では時制が合いません。',
        ),
        (
            'A : You ( ) read this book before the test next Monday.\n'
            'B : OK, Mr. Peterson.',
            ['have', 'be', 'must', 'were'],
            'テスト前に読む必要がある、という指示なので「must」が自然です。'
            '「have / be / were」だけでは義務の意味になりません。',
        ),
    ]
    parts = []
    for i, (q, choices, expl) in enumerate(items):
        n = start + i
        ans = RW[i + 1]
        parts.append(_grammar_block(n, q, choices, ans, expl))
    return '\n---\n\n'.join(parts)


def conversation_blocks(start: int = 56) -> str:
    items = [
        (
            'Girl: I forgot my red pen. ( )\n'
            'Boy: Of course you can. Here you are.',
            [
                'Will you go home soon?',
                'Is the color OK?',
                'Do you like writing?',
                'Can I borrow yours?',
            ],
            '相手が「もちろんいいよ。はいどうぞ」と返すので、'
            '借りる依頼「Can I borrow yours?」が自然です。'
            '帰宅・色・好みの質問ではこの返事と合いません。',
        ),
        (
            'Girl 1: I want to climb this tree.\n'
            'Girl 2: ( ) Let’s climb the one over there.\n'
            'Girl 1: OK.',
            [
                'These flowers are pretty.',
                'It’s too tall.',
                'My garden is big.',
                'Your house is very nice.',
            ],
            '別の木を提案しているので、今の木が「It’s too tall.（高すぎる）」が自然です。'
            '花・庭・家のほめ言葉では別の木へ移す理由になりません。',
        ),
        (
            'Man: Excuse me. I want to buy these socks. ( )\n'
            'Clerk: Two dollars.',
            [
                'How are you doing?',
                'How many do you have?',
                'How tall are you?',
                'How much are they?',
            ],
            '店員が値段を答えるので「How much are they?」が自然です。'
            'あいさつ・個数・身長の質問では「2ドル」の答えと合いません。',
        ),
        (
            'Daughter: Dad, I can’t find my social studies textbook.\n'
            'Father: ( )\n'
            'Daughter: Thanks.',
            [
                'It’s a difficult subject.',
                'It was very interesting.',
                'It’s on the kitchen table.',
                'It’s for your brother.',
            ],
            '見つからない教科書の場所を教える「It’s on the kitchen table.」が自然です。'
            '科目の感想や持ち主の話では「Thanks」への助けになりにくいです。',
        ),
        (
            'Girl 1: Jenny, you don’t look well today. ( )\n'
            'Girl 2: I’m fine. I’m just a little tired.',
            [
                'Can I go home?',
                'Did you call me?',
                'Are you OK?',
                'Is your mother a doctor?',
            ],
            '顔色を心配したあとに「大丈夫？」と聞く「Are you OK?」が自然です。'
            '帰宅許可・電話・母親の職業はこの返事とつながりません。',
        ),
    ]
    parts = []
    for i, (q, choices, expl) in enumerate(items):
        n = start + i
        ans = RW[16 + i]
        parts.append(_conv_block(n, q, choices, ans, expl))
    return '\n---\n\n'.join(parts)


def wordorder_blocks(start: int = 26) -> str:
    items = [
        (
            'なぜあなたは今朝、そんなに早く起きたのですか。\n'
            '① you ② up ③ get ④ why ⑤ did\n'
            '( ) [2番目] ( ) [4番目] ( ) so early this morning?',
            ['① ─ ②', '⑤ ─ ③', '③ ─ ⑤', '④ ─ ①'],
            'Why did you get up so early this morning?\n'
            '疑問詞＋did＋主語＋動詞原形の語順なので、2番目は did、4番目は get です。',
        ),
        (
            '今日の午後、あなたに電話してもいいですか。\n'
            '① this ② may ③ you ④ I ⑤ call\n'
            '( ) [2番目] ( ) [4番目] ( ) afternoon?',
            ['④ ─ ③', '① ─ ③', '⑤ ─ ①', '③ ─ ①'],
            'May I call you this afternoon?\n'
            '許可の依頼は May + I + 動詞原形 なので、2番目は I、4番目は you です。',
        ),
        (
            'ネパールではたくさんの高い山を見ることができます。\n'
            '① see ② you ③ can ④ high mountains ⑤ lots of\n'
            '( ) [2番目] ( ) [4番目] ( ) in Nepal.',
            ['④ ─ ②', '③ ─ ⑤', '④ ─ ③', '⑤ ─ ③'],
            'You can see lots of high mountains in Nepal.\n'
            'can + 動詞原形の語順なので、2番目は can、4番目は lots of です。',
        ),
        (
            '私は毎朝７時に家を出て学校へ向かいます。\n'
            '① at ② school ③ leave ④ for ⑤ home\n'
            'I ( ) [2番目] ( ) [4番目] ( ) seven o’clock every morning.',
            ['⑤ ─ ③', '③ ─ ④', '⑤ ─ ②', '③ ─ ⑤'],
            'I leave home for school at seven o’clock every morning.\n'
            'leave home for school の語順なので、2番目は home、4番目は school です。',
        ),
        (
            'これらのコーヒーカップを洗ってくれますか。\n'
            '① wash ② you ③ coffee cups ④ could ⑤ these\n'
            '( ) [2番目] ( ) [4番目] ( ), please?',
            ['④ ─ ⑤', '③ ─ ①', '② ─ ⑤', '① ─ ②'],
            'Could you wash these coffee cups, please?\n'
            'Could you + 動詞原形 の語順なので、2番目は you、4番目は these です。',
        ),
    ]
    parts = []
    for i, (q, choices, expl) in enumerate(items):
        n = start + i
        ans = RW[21 + i]
        parts.append(
            f'問題{n}:\n{q}\n\n'
            f'選択肢{n}:\n{_choice_lines(choices)}\n\n'
            f'【正解{n}】\n{ans}. {choices[ans - 1]}\n\n'
            f'【解説{n}】\n{expl}\n'
        )
    return '\n---\n\n'.join(parts)


def reading_blocks(start_passage: int = 13) -> str:
    p13 = start_passage
    p14 = start_passage + 1
    p15 = start_passage + 2
    a_text = (
        'A Musician Will Visit Our School\n\n'
        'The famous piano player Mr. Stevens will visit the school on Friday afternoon for one hour.\n\n'
        'He will first give a speech in the gym and then play three songs in the music room. '
        'After this performance, students can eat snacks in the cafeteria.\n\n'
        'Date: February 12\n'
        'Time: 4:00 p.m. to 5:00 p.m.'
    )
    a_qs = [
        (
            'What will happen in the gym?',
            [
                'A piano player will give a speech.',
                'Students will receive free snacks.',
                'A piano player will play songs.',
                'Students will dance.',
            ],
            1,
            '本文に「give a speech in the gym」とあります。演奏は music room、おやつは cafeteria です。',
        ),
        (
            'How many songs will Mr. Stevens play?',
            ['Two songs.', 'Three songs.', 'Four songs.', 'Five songs.'],
            2,
            '「play three songs in the music room」と明記されています。2・4・5曲という記述はありません。',
        ),
    ]
    b_text = (
        'From: Jimmy Cook\n'
        'To: Cathy Cook\n'
        'Date: July 7\n'
        'Subject: How are your cats?\n\n'
        'Dear Grandma,\n'
        'Last summer was so much fun! I enjoyed spending two weeks at your home. '
        'How is your cat, Lily? She had some babies, right? Dad told me about it. '
        'How many babies does she have? I really want to see them! '
        'Can I visit your home next month? I can stay for four days then!\n'
        'Write soon,\n'
        'Jimmy\n\n'
        '-\n\n'
        'From: Cathy Cook\n'
        'To: Jimmy Cook\n'
        'Date: July 7\n'
        'Subject: They are fine!\n\n'
        'Dear Jimmy,\n'
        'Of course, come and see my cat Lily and her babies next month! '
        'She has three babies, and they are very cute. '
        'Yesterday, one of my friends visited me and saw them, too! '
        'I’ll send you a picture of the babies by email tomorrow!\n'
        'Love,\n'
        'Grandma'
    )
    b_qs = [
        (
            'When can Jimmy visit his grandmother’s home?',
            ['Tomorrow.', 'Next week.', 'Next month.', 'Next summer.'],
            3,
            'Jimmy が「next month」に訪れてよいか尋ね、祖母も「next month」と返事しています。',
        ),
        (
            'How many babies does Lily have?',
            ['One.', 'Two.', 'Three.', 'Four.'],
            3,
            '祖母のメールに「She has three babies」とあります。',
        ),
        (
            'Who visited Jimmy’s grandmother yesterday?',
            ['Her friend.', 'Her daughter.', 'Jimmy.', 'Jimmy’s father.'],
            1,
            '「Yesterday, one of my friends visited me」とあるので、訪問者は祖母の友人です。',
        ),
    ]
    c_text = (
        'A Visit to a History Museum\n\n'
        'George is thirteen years old. Recently, his sister wanted to go to a history museum. '
        'So, his family went to the museum last Saturday. The museum was in an old building. '
        'It was eighty years old. In the museum, he saw many interesting things. '
        'The best part was an old classroom.\n\n'
        'George walked into the classroom and saw an old blackboard. '
        'The blackboard was forty years old. He was surprised because the blackboard was green. '
        'He also saw desks and chairs. They were dark brown. '
        'Then, George saw some old history textbooks. '
        'He saw a lot of interesting things in the classroom. '
        'He liked looking at the textbooks most because they were so old.\n\n'
        'The history museum was very fun. George’s favorite subjects in school were English and math before, '
        'but now his favorite is history. George wants to go to more museums with his sister.'
    )
    c_qs = [
        (
            'Why did George’s family go to the museum last Saturday?',
            [
                'George’s father had four tickets.',
                'George’s mother works there.',
                'George’s sister wanted to go.',
                'George likes history.',
            ],
            3,
            '「his sister wanted to go to a history museum. So, his family went…」と因果が書かれています。',
        ),
        (
            'How old was the blackboard?',
            [
                'Thirteen years old.',
                'Twenty years old.',
                'Forty years old.',
                'Eighty years old.',
            ],
            3,
            '「The blackboard was forty years old」とあります。建物の80年と混同しないようにします。',
        ),
        (
            'What color were the desks?',
            ['Black.', 'Green.', 'Light brown.', 'Dark brown.'],
            4,
            '机と椅子は「They were dark brown」とあります。黒板が緑なのは別情報です。',
        ),
        (
            'What did George like most in the classroom?',
            ['The textbooks.', 'The desks.', 'The map.', 'The blackboard.'],
            1,
            '「He liked looking at the textbooks most」と明記されています。',
        ),
        (
            'Now, George’s favorite subject is',
            ['math.', 'English.', 'history.', 'music.'],
            3,
            '以前は English and math が好きだったが、「now his favorite is history」とあります。',
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
            fmt_passage(p13, a_text, a_qs),
            fmt_passage(p14, b_text, b_qs),
            fmt_passage(p15, c_text, c_qs),
        ]
    )


def listening_illustration_blocks(start: int = 41) -> str:
    # script dialogues + official choices order
    items = [
        (
            'W: Hi, Brian.\n'
            'M: Hi, Sally. Do you want to watch a soccer game this Saturday?\n'
            'W: Sure. What time does it start?',
            ['At 1:30.', 'On Saturday.', 'Let’s go now.'],
            '最後に開始時刻を聞いているので、1「At 1:30.（1時半。）」が自然です。'
            '2は曜日、3は今すぐ行こう、で時刻の答えになりません。',
        ),
        (
            'M: Let’s have lunch today.\n'
            'W: Sure, but I have a meeting until noon.\n'
            'M: How about 12:30, then?',
            ['It’s near here.', 'With Mr. Wilson.', 'That’s fine.'],
            '昼食の時間提案への返事なので、3「That’s fine.（それでいいよ。）」が自然です。'
            '場所や同席者の話はこの提案への応答として合いません。',
        ),
        (
            'W: Do we have any meetings today?\n'
            'M: Yes, we have one with Alan and Janet this afternoon.\n'
            'W: OK. Anything else?',
            ['At twelve o’clock.', 'No, that’s all.', 'Yes, he did.'],
            '他にあるかと聞かれているので、2「No, that’s all.（いいえ、それだけです。）」が自然です。'
            '時刻や「彼がした」はこの質問に合いません。',
        ),
        (
            'W: Excuse me.\n'
            'M: How can I help you?\n'
            'W: Where are the women’s shoes?',
            ['On the third floor.', 'At six o’clock.', 'I’ll buy them.'],
            '場所を尋ねているので、1「On the third floor.（3階です。）」が自然です。'
            '時刻や買う意思は場所の答えになりません。',
        ),
        (
            'W: What time does your volleyball practice start on Saturday?\n'
            'M: At 9 a.m.\n'
            'W: Will you come home by noon?',
            ['I think so.', 'Twice a day.', 'It’s my ball.'],
            '正午までに帰るかへの返事なので、1「I think so.（多分そうだよ。）」が自然です。'
            '回数やボールの所有はこの質問に合いません。',
        ),
        (
            'M: Are you hungry?\n'
            'W: Not really.\n'
            'M: Do you want some coffee?',
            ['That sounds nice.', 'Chicken, please.', 'In cooking class.'],
            'コーヒーを勧める提案への返事なので、1「That sounds nice.（いいね。）」が自然です。'
            'チキンや料理の授業はこの誘いへの答えになりません。',
        ),
        (
            'W: Is it raining outside?\n'
            'M: No, but the sky is dark.\n'
            'W: Take your umbrella with you.',
            ['No, you won’t.', 'Since this morning.', 'All right, Mom.'],
            '傘を持って行くよう言われての返事なので、3「All right, Mom.（わかった、お母さん。）」が自然です。'
            '否定や開始時刻はこの指示への返事として合いません。',
        ),
        (
            'M: I’m going to the beach with my brother.\n'
            'W: That sounds good!\n'
            'M: Do you have any brothers or sisters?',
            ['I don’t have any.', 'No. I can’t swim.', 'Next week.'],
            '兄弟姉妹がいるかへの答えなので、1「I don’t have any.（いないよ。）」が自然です。'
            '泳げない・来週は人数の質問に答えません。',
        ),
        (
            'W: Good morning, Mr. Lee.\n'
            'M: Hi. Where are you going?\n'
            'W: To the library.',
            ['It’s late at night.', 'I studied science.', 'Have a nice day.'],
            '行き先を聞いたあとの自然な返答は、3「Have a nice day.（よい一日を。）」です。'
            '夜遅い・勉強した、はこの場面のあいさつとして弱くなります。',
        ),
        (
            'M: How was your sister’s birthday?\n'
            'W: We had a big party.\n'
            'M: Did she like it?',
            [
                'I like chocolate cake.',
                'Yes. She got many presents.',
                'Thank you for coming.',
            ],
            '気に入ったかへの答えなので、2「Yes. She got many presents.（うん。たくさんプレゼントをもらったよ。）」が自然です。'
            '自分の好みや来てくれてありがとうはこの質問への直接の答えになりません。',
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
            'W: Did you finish your report, Max?\n'
            'M: Yes. I put it on your desk.\n'
            'W: Really? I can’t find it.\n'
            'M: Oh no.',
            'What is the woman’s problem?',
            [
                'She can’t find the report.',
                'She forgot to call Max.',
                'The report is too long.',
                'Her desk is broken.',
            ],
            '女性が「I can’t find it」と言っているので、1が正解です。',
        ),
        (
            'W: How was your weekend, Ken?\n'
            'M: Not so good. My mom was sick, so my dad took her to the doctor.\n'
            'W: Is she OK now?\n'
            'M: Yes, she’s much better.',
            'Who was sick?',
            ['Ken.', 'Ken’s mother.', 'Ken’s father.', 'Ken’s friend.'],
            '「My mom was sick」とあるので、2「Ken’s mother」が正解です。',
        ),
        (
            'W: Hi, Joe. Is that a new camera?\n'
            'M: Yes, Kim. My dad gave it to me.\n'
            'W: Do you like it?\n'
            'M: Yeah, it’s great. I just took some pictures of my friends.',
            'Who did Joe take pictures of?',
            ['Kim’s friends.', 'Kim’s father.', 'His friends.', 'His father.'],
            '「pictures of my friends」なので、3「His friends」が正解です。',
        ),
        (
            'W: Where are you going?\n'
            'M: I’m going to the hospital.\n'
            'W: Why? Are you sick?\n'
            'M: No. My grandmother broke her leg, so I’m going to visit her.',
            'Why is the man going to the hospital?',
            [
                'Because he is sick.',
                'Because he broke his leg.',
                'To talk to his doctor.',
                'To visit his grandmother.',
            ],
            '祖母のお見舞いだと明言しているので、4が正解です。',
        ),
        (
            'W: Did you start writing your history report today?\n'
            'M: No. How about you?\n'
            'W: No. We need to finish them by Friday.\n'
            'M: I’ll write mine before class tomorrow.',
            'What do they need to do by Friday?',
            [
                'Take a test.',
                'Talk to their history teacher.',
                'Clean their classroom.',
                'Finish their reports.',
            ],
            '「finish them by Friday」の them は history report なので、4が正解です。',
        ),
        (
            'W: You can pick one toy from here.\n'
            'M: I want a toy car.\n'
            'W: You already have one. How about another toy?\n'
            'M: No, I like cars.',
            'Which toy does the boy want?',
            ['A toy dog.', 'A robot.', 'A toy car.', 'A toy plane.'],
            '何度も車のおもちゃを望んでいるので、3が正解です。',
        ),
        (
            'M: You have a baseball game today, right?\n'
            'W: Yes. I also have a soccer game on Wednesday.\n'
            'M: Is your tennis game on Friday?\n'
            'W: That’s right.',
            'Which game does the girl have today?',
            [
                'A tennis game.',
                'A soccer game.',
                'A basketball game.',
                'A baseball game.',
            ],
            '今日は baseball game だと確認しているので、4が正解です。',
        ),
        (
            'M: You have a dog, right, Mia?\n'
            'W: Yes, I do.\n'
            'M: What other pets do you have?\n'
            'W: A cat and a bird. So I have three pets.',
            'How many pets does Mia have?',
            ['One.', 'Two.', 'Three.', 'Four.'],
            '「I have three pets」とあるので、3が正解です。',
        ),
        (
            'M: Can we go to a Japanese restaurant for dinner?\n'
            'W: No, I had Japanese food for lunch.\n'
            'M: Where should we go?\n'
            'W: Let’s go to an Italian restaurant.',
            'Where will they go for dinner?',
            [
                'To a Chinese restaurant.',
                'To a Japanese restaurant.',
                'To a Spanish restaurant.',
                'To an Italian restaurant.',
            ],
            '夕食は Italian restaurant に行くと決まっているので、4が正解です。',
        ),
        (
            'W: Can we study together today?\n'
            'M: I can’t. I have a meeting at the library.\n'
            'W: How about tomorrow? We can meet at school.\n'
            'M: OK. Let’s meet at two.',
            'Where will they meet tomorrow?',
            [
                'At school.',
                'At the girl’s house.',
                'At the library.',
                'At the boy’s house.',
            ],
            '明日は「meet at school」なので、1が正解です。図書館は今日の予定です。',
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
            'W: Emma enjoys shopping. This weekend she will go to the new shopping center with her friend. '
            'She is going to buy a birthday present for her mother.',
            'What will Emma do this weekend?',
            [
                'Visit her friend.',
                'Go shopping.',
                'Go to a party.',
                'Make a cake.',
            ],
            '週末に新しいショッピングセンターへ行くので、2「Go shopping」が正解です。',
        ),
        (
            'W: My parents and I went to my favorite curry restaurant last night. '
            'It’s near our house. The vegetable curry is really good.',
            'What is the girl talking about?',
            [
                'Her vegetable garden.',
                'A cooking class.',
                'A restaurant.',
                'Her new house.',
            ],
            '好きなカレー店の話なので、3「A restaurant」が正解です。',
        ),
        (
            'M: Kathy and Mary play tennis together on Saturday mornings. '
            'Today, it rained, so they went to a shopping mall. They bought some books there.',
            'What did Kathy and Mary do today?',
            [
                'They played tennis.',
                'They saw a movie.',
                'They went shopping.',
                'They went to the library.',
            ],
            '今日は雨でモールへ行き本を買ったので、3「They went shopping」が正解です。',
        ),
        (
            'M: After school, I often go to my friend Andrew’s house, and we study together. '
            'Sometimes we play computer games, too. Andrew has lots of great games.',
            'Where does the boy often go after school?',
            [
                'To the library.',
                'To a big game.',
                'To the computer club.',
                'To his friend’s house.',
            ],
            'よく Andrew の家へ行くとあるので、4が正解です。',
        ),
        (
            'M: Wendy had a party at her house yesterday. She made pasta, and her husband made vegetable soup. '
            'Her friend Julie brought drinks and cake.',
            'Who made vegetable soup?',
            ['Wendy.', 'Wendy’s husband.', 'Julie.', 'Julie’s husband.'],
            '「her husband made vegetable soup」なので、2が正解です。',
        ),
        (
            'M: Emi likes reading. She often goes to the library. '
            'Today, she will read a book at home after school.',
            'What will Emi do today?',
            [
                'Go to the library.',
                'Help her mother.',
                'Call her friend.',
                'Read a book at home.',
            ],
            '今日は家で本を読むとあるので、4が正解です。図書館はよく行く場所です。',
        ),
        (
            'M: Jack usually plays soccer or rides his bike with his friends after school. '
            'But it rained yesterday, so he stayed at home and read books in the afternoon.',
            'What did Jack do yesterday afternoon?',
            [
                'He read books.',
                'He rode his bike.',
                'He played soccer.',
                'He did his homework.',
            ],
            '昨日の午後は家で本を読んだので、1が正解です。',
        ),
        (
            'W: Yesterday, my father made lunch for Anna and me. My mother and brother were not home. '
            'My grandmother came to visit me, so I cleaned my house. Anna helped me.',
            'What did the girl do yesterday?',
            [
                'She made lunch.',
                'She visited her grandmother.',
                'She cleaned her house.',
                'She met Anna’s father.',
            ],
            '祖母が来るので家を掃除した、とあるので、3が正解です。昼食を作ったのは父親です。',
        ),
        (
            'M: Jack usually rides his bike to school when the weather is nice. '
            'When it is rainy, Jack’s father takes him to school by car.',
            'How does Jack usually go to school?',
            ['By bike.', 'By bus.', 'By train.', 'By car.'],
            '天気がよいときは自転車、と「usually」があるので、1が正解です。車は雨のときです。',
        ),
        (
            'W: Welcome to the city art museum. The fees are three dollars for kids, '
            'five dollars for junior high school students, and ten dollars for adults.',
            'How much is the fee for adults?',
            [
                'Three dollars.',
                'Five dollars.',
                'Eight dollars.',
                'Ten dollars.',
            ],
            '大人は ten dollars なので、4が正解です。',
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
    _append(_Q / 'grammar_fill_questions.txt', grammar_blocks(166))
    _append(_Q / 'conversation_questions.txt', conversation_blocks(56))
    _append(_Q / 'wordorder_questions.txt', wordorder_blocks(26))
    _append(_Q / 'reading_comprehesion_questions.txt', reading_blocks(13))
    _append(_Q / 'listening_illustration_questions.txt', listening_illustration_blocks(41))
    _append(_Q / 'listening_conversation_questions.txt', listening_conversation_blocks(41))
    _append(_Q / 'listening_passage_questions.txt', listening_passage_blocks(41))
    print('done')


if __name__ == '__main__':
    main()
