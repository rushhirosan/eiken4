#!/usr/bin/env python3
"""
4級 2026①追記分（リスニング41–50）の解説を既存トーンに揃える。

- 放送文に日本語訳（…）を付与
- Question に日本語訳を付与
- 正解根拠 + 外れ選択肢の短い却下理由
"""
from __future__ import annotations

import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_Q = _REPO / 'data' / 'questions'

# (start_q, end_q) inclusive replacements: full 【解説N】... body (without header)
CONVERSATION_EXPL = {
    41: """放送文
W: Did you finish your report, Max?（マックス、レポートは終わった？）
M: Yes. I put it on your desk.（うん。君の机に置いたよ。）
W: Really? I can’t find it.（本当？見つからないんだけど。）
M: Oh no.（えっ、まずい。）
Question: What is the woman’s problem?（女性の困りごとは何ですか？）

女性が「I can’t find it（見つからない）」と言っているので、1「She can’t find the report.（レポートが見つからない。）」が正解です。
2「She forgot to call Max.（マックスに電話するのを忘れた。）」・3「The report is too long.（レポートが長すぎる。）」・4「Her desk is broken.（机が壊れている。）」は会話に出ていません。
""",
    42: """放送文
W: How was your weekend, Ken?（ケン、週末はどうだった？）
M: Not so good. My mom was sick, so my dad took her to the doctor.（あまりよくなかった。お母さんが具合悪くて、お父さんが病院に連れていったんだ。）
W: Is she OK now?（今は大丈夫？）
M: Yes, she’s much better.（うん、かなりよくなったよ。）
Question: Who was sick?（誰が具合悪かったですか？）

「My mom was sick（お母さんが具合悪かった）」とあるので、2「Ken’s mother.（ケンのお母さん。）」が正解です。
1「Ken.」は話者自身ではなく、3「Ken’s father.」は病院へ連れていった人、4「Ken’s friend.」は会話に出てきません。
""",
    43: """放送文
W: Hi, Joe. Is that a new camera?（ジョー、それ新しいカメラ？）
M: Yes, Kim. My dad gave it to me.（うん、キム。お父さんがくれたんだ。）
W: Do you like it?（気に入った？）
M: Yeah, it’s great. I just took some pictures of my friends.（うん、最高。さっき友達の写真を撮ったんだ。）
Question: Who did Joe take pictures of?（ジョーは誰の写真を撮りましたか？）

「pictures of my friends（友達の写真）」とあるので、3「His friends.（彼の友達。）」が正解です。
1「Kim’s friends.」・2「Kim’s father.」・4「His father.」は撮った相手ではありません（父はカメラをくれた人です）。
""",
    44: """放送文
W: Where are you going?（どこへ行くの？）
M: I’m going to the hospital.（病院へ行くよ。）
W: Why? Are you sick?（どうして？具合悪いの？）
M: No. My grandmother broke her leg, so I’m going to visit her.（ううん。おばあちゃんが足を折ったから、お見舞いに行くんだ。）
Question: Why is the man going to the hospital?（男性が病院へ行く理由は何ですか？）

「I’m going to visit her（お見舞いに行く）」とあるので、4「To visit his grandmother.（祖母のお見舞い。）」が正解です。
1「Because he is sick.」は否定され、2「Because he broke his leg.」は祖母のけが、3「To talk to his doctor.」は会話に出てきません。
""",
    45: """放送文
W: Did you start writing your history report today?（今日、歴史のレポート書き始めた？）
M: No. How about you?（ううん。君は？）
W: No. We need to finish them by Friday.（私も。金曜日までに仕上げなきゃ。）
M: I’ll write mine before class tomorrow.（明日の授業前に書くよ。）
Question: What do they need to do by Friday?（2人は金曜日までに何をしなければなりませんか？）

「finish them by Friday」の them は history report なので、4「Finish their reports.（レポートを仕上げる。）」が正解です。
1「Take a test.」・2「Talk to their history teacher.」・3「Clean their classroom.」は会話に出てきません。
""",
    46: """放送文
W: You can pick one toy from here.（ここからおもちゃを1つ選んでいいよ。）
M: I want a toy car.（車のおもちゃがほしい。）
W: You already have one. How about another toy?（もう持ってるでしょ。別のおもちゃは？）
M: No, I like cars.（ううん、車が好きなんだ。）
Question: Which toy does the boy want?（男の子はどのおもちゃがほしいですか？）

「I want a toy car」「I like cars」と車にこだわっているので、3「A toy car.（車のおもちゃ。）」が正解です。
1「A toy dog.」・2「A robot.」・4「A toy plane.」は会話に出ていません。
""",
    47: """放送文
M: You have a baseball game today, right?（今日野球の試合だよね？）
W: Yes. I also have a soccer game on Wednesday.（うん。水曜にはサッカーの試合もあるよ。）
M: Is your tennis game on Friday?（テニスの試合は金曜？）
W: That’s right.（そうだよ。）
Question: Which game does the girl have today?（女の子の今日の試合はどれですか？）

今日は「baseball game」だと確認しているので、4「A baseball game.（野球の試合。）」が正解です。
2「A soccer game.」は水曜、1「A tennis game.」は金曜、3「A basketball game.」は会話に出てきません。
""",
    48: """放送文
M: You have a dog, right, Mia?（ミア、犬を飼ってるよね？）
W: Yes, I do.（うん。）
M: What other pets do you have?（ほかにどんなペットがいるの？）
W: A cat and a bird. So I have three pets.（猫と鳥。だから3匹いるよ。）
Question: How many pets does Mia have?（ミアのペットは何匹ですか？）

「I have three pets（3匹いる）」とあるので、3「Three.（3匹。）」が正解です。
犬だけなら1、猫と鳥を足し忘れると数が合わず、4「Four.」は多すぎます。
""",
    49: """放送文
M: Can we go to a Japanese restaurant for dinner?（夕食は日本食の店に行こうか？）
W: No, I had Japanese food for lunch.（ううん、お昼に日本食を食べたの。）
M: Where should we go?（じゃあどこに行く？）
W: Let’s go to an Italian restaurant.（イタリアンに行こう。）
Question: Where will they go for dinner?（2人は夕食にどこへ行きますか？）

夕食は「Italian restaurant」に行くと決まっているので、4「To an Italian restaurant.（イタリア料理店へ。）」が正解です。
2「To a Japanese restaurant.」は昼食の話で否定され、1「Chinese」・3「Spanish」は会話に出てきません。
""",
    50: """放送文
W: Can we study together today?（今日いっしょに勉強できる？）
M: I can’t. I have a meeting at the library.（無理。図書館で用事があるんだ。）
W: How about tomorrow? We can meet at school.（じゃあ明日は？学校で会えるよ。）
M: OK. Let’s meet at two.（いいよ。2時に会おう。）
Question: Where will they meet tomorrow?（2人は明日どこで会いますか？）

明日は「meet at school（学校で会う）」なので、1「At school.（学校で。）」が正解です。
3「At the library.」は今日の予定、2・4の家は会話に出てきません。
""",
}

PASSAGE_EXPL = {
    41: """放送文
W: Emma enjoys shopping. This weekend she will go to the new shopping center with her friend. She is going to buy a birthday present for her mother.（エマは買い物が好きです。今週末、友達と新しいショッピングセンターへ行きます。お母さんの誕生日プレゼントを買う予定です。）
Question: What will Emma do this weekend?（エマは今週末何をしますか？）

週末にショッピングセンターへ行くので、2「Go shopping.（買い物に行く。）」が正解です。
1「Visit her friend.」は一緒に行く相手の話で目的ではなく、3「Go to a party.」・4「Make a cake.」は話に出てきません。
""",
    42: """放送文
W: My parents and I went to my favorite curry restaurant last night. It’s near our house. The vegetable curry is really good.（昨夜、両親と好きなカレー店へ行きました。家の近くです。野菜カレーがとてもおいしいです。）
Question: What is the girl talking about?（女の子は何について話していますか？）

好きなカレー店の話なので、3「A restaurant.（レストラン。）」が正解です。
1「Her vegetable garden.」・2「A cooking class.」・4「Her new house.」は話題の中心ではありません。
""",
    43: """放送文
M: Kathy and Mary play tennis together on Saturday mornings. Today, it rained, so they went to a shopping mall. They bought some books there.（キャシーとメアリーは土曜の朝にテニスをします。今日は雨だったのでショッピングモールへ行き、そこで本を買いました。）
Question: What did Kathy and Mary do today?（キャシーとメアリーは今日何をしましたか？）

今日は雨でモールへ行き本を買ったので、3「They went shopping.（買い物をした。）」が正解です。
1「They played tennis.」はいつもの土曜の話、2「They saw a movie.」・4「They went to the library.」は出ていません。
""",
    44: """放送文
M: After school, I often go to my friend Andrew’s house, and we study together. Sometimes we play computer games, too. Andrew has lots of great games.（放課後、よく友達のアンドリューの家へ行っていっしょに勉強します。ときどきコンピュータゲームもします。彼はすごいゲームをたくさん持っています。）
Question: Where does the boy often go after school?（男の子は放課後よくどこへ行きますか？）

よく「Andrew’s house」へ行くとあるので、4「To his friend’s house.（友達の家へ。）」が正解です。
1「To the library.」・2「To a big game.」・3「To the computer club.」は会話の中心ではありません。
""",
    45: """放送文
M: Wendy had a party at her house yesterday. She made pasta, and her husband made vegetable soup. Her friend Julie brought drinks and cake.（昨日ウェンディは家でパーティーをしました。彼女がパスタを作り、ご主人が野菜スープを作りました。友達のジュリーが飲み物とケーキを持ってきました。）
Question: Who made vegetable soup?（野菜スープを作ったのは誰ですか？）

「her husband made vegetable soup」なので、2「Wendy’s husband.（ウェンディの夫。）」が正解です。
1「Wendy.」はパスタ、3「Julie.」は飲み物とケーキ、4「Julie’s husband.」は話に出てきません。
""",
    46: """放送文
M: Emi likes reading. She often goes to the library. Today, she will read a book at home after school.（エミは読書が好きです。よく図書館へ行きます。今日は放課後、家で本を読みます。）
Question: What will Emi do today?（エミは今日何をしますか？）

今日は「read a book at home」とあるので、4「Read a book at home.（家で本を読む。）」が正解です。
1「Go to the library.」はよく行く場所で今日の予定ではなく、2・3は会話に出てきません。
""",
    47: """放送文
M: Jack usually plays soccer or rides his bike with his friends after school. But it rained yesterday, so he stayed at home and read books in the afternoon.（ジャックは放課後、いつも友達とサッカーをしたり自転車に乗ったりします。でも昨日は雨だったので、家にいて午後は本を読みました。）
Question: What did Jack do yesterday afternoon?（ジャックは昨日の午後何をしましたか？）

昨日の午後は家で本を読んだので、1「He read books.（本を読んだ。）」が正解です。
2「He rode his bike.」・3「He played soccer.」はいつもの行動、4「He did his homework.」は話に出てきません。
""",
    48: """放送文
W: Yesterday, my father made lunch for Anna and me. My mother and brother were not home. My grandmother came to visit me, so I cleaned my house. Anna helped me.（昨日、お父さんがアンナと私の昼食を作りました。お母さんと弟はいませんでした。おばあちゃんが訪ねてくるので家を掃除しました。アンナが手伝ってくれました。）
Question: What did the girl do yesterday?（女の子は昨日何をしましたか？）

「I cleaned my house」とあるので、3「She cleaned her house.（家を掃除した。）」が正解です。
1「She made lunch.」は父親、2「She visited her grandmother.」は祖母が来た話で逆、4「She met Anna’s father.」は出てきません。
""",
    49: """放送文
M: Jack usually rides his bike to school when the weather is nice. When it is rainy, Jack’s father takes him to school by car.（ジャックは天気がよいとき、いつも自転車で学校へ行きます。雨のときはお父さんが車で送ってくれます。）
Question: How does Jack usually go to school?（ジャックは普段どうやって学校へ行きますか？）

「usually rides his bike」とあるので、1「By bike.（自転車で。）」が正解です。
4「By car.」は雨のとき、2「By bus.」・3「By train.」は話に出てきません。
""",
    50: """放送文
W: Welcome to the city art museum. The fees are three dollars for kids, five dollars for junior high school students, and ten dollars for adults.（市立美術館へようこそ。料金は子ども3ドル、中学生5ドル、大人10ドルです。）
Question: How much is the fee for adults?（大人の料金はいくらですか？）

大人は「ten dollars」なので、4「Ten dollars.（10ドル。）」が正解です。
1「Three dollars.」は子ども、2「Five dollars.」は中学生、3「Eight dollars.」は話に出てきません。
""",
}

ILLUSTRATION_EXPL = {
    41: """放送文
W: Hi, Brian.（こんにちは、ブライアン。）
M: Hi, Sally. Do you want to watch a soccer game this Saturday?（こんにちは、サリー。今週の土曜にサッカーの試合を見ない？）
W: Sure. What time does it start?（いいよ。何時に始まるの？）

最後に開始時刻を聞いているので、1「At 1:30.（1時半。）」が自然です。
2「On Saturday.（土曜日に。）」は曜日、3「Let’s go now.（今行こう。）」は今すぐで、時刻の答えになりません。
""",
    42: """放送文
M: Let’s have lunch today.（今日ランチにしよう。）
W: Sure, but I have a meeting until noon.（いいけど、正午まで会議があるの。）
M: How about 12:30, then?（じゃあ12時半はどう？）

昼食の時間提案への返事なので、3「That’s fine.（それでいいよ。）」が自然です。
1「It’s near here.（ここから近いよ。）」は場所、2「With Mr. Wilson.（ウィルソンさんと。）」は同席者で、提案への応答として合いません。
""",
    43: """放送文
W: Do we have any meetings today?（今日会議はある？）
M: Yes, we have one with Alan and Janet this afternoon.（うん、午後にアランとジャネットとあるよ。）
W: OK. Anything else?（わかった。ほかには？）

他にあるかと聞かれているので、2「No, that’s all.（いいえ、それだけです。）」が自然です。
1「At twelve o’clock.（12時に。）」は時刻、3「Yes, he did.（はい、彼はしました。）」はこの質問に合いません。
""",
    44: """放送文
W: Excuse me.（すみません。）
M: How can I help you?（どうされましたか？）
W: Where are the women’s shoes?（婦人靴売り場はどこですか？）

場所を尋ねているので、1「On the third floor.（3階です。）」が自然です。
2「At six o’clock.（6時に。）」は時刻、3「I’ll buy them.（買います。）」は買う意思で、場所の答えになりません。
""",
    45: """放送文
W: What time does your volleyball practice start on Saturday?（土曜のバレーの練習は何時に始まるの？）
M: At 9 a.m.（午前9時だよ。）
W: Will you come home by noon?（正午までに帰ってくる？）

正午までに帰るかへの返事なので、1「I think so.（多分そうだよ。）」が自然です。
2「Twice a day.（1日2回。）」は回数、3「It’s my ball.（それは私のボールだよ。）」はこの質問に合いません。
""",
    46: """放送文
M: Are you hungry?（お腹空いてる？）
W: Not really.（あまり。）
M: Do you want some coffee?（コーヒーはどう？）

コーヒーを勧める提案への返事なので、1「That sounds nice.（いいね。）」が自然です。
2「Chicken, please.（チキンをお願い。）」・3「In cooking class.（料理の授業で。）」はこの誘いへの答えになりません。
""",
    47: """放送文
W: Is it raining outside?（外は雨？）
M: No, but the sky is dark.（ううん、でも空が暗いよ。）
W: Take your umbrella with you.（傘を持って行きなさい。）

傘を持って行くよう言われての返事なので、3「All right, Mom.（わかった、お母さん。）」が自然です。
1「No, you won’t.（いいえ、そうはならないよ。）」・2「Since this morning.（今朝から。）」はこの指示への返事として合いません。
""",
    48: """放送文
M: I’m going to the beach with my brother.（弟とビーチに行くよ。）
W: That sounds good!（いいね！）
M: Do you have any brothers or sisters?（兄弟姉妹はいる？）

兄弟姉妹がいるかへの答えなので、1「I don’t have any.（いないよ。）」が自然です。
2「No. I can’t swim.（ううん、泳げないんだ。）」・3「Next week.（来週。）」は人数の質問に答えません。
""",
    49: """放送文
W: Good morning, Mr. Lee.（おはようございます、リーさん。）
M: Hi. Where are you going?（こんにちは。どこへ行くの？）
W: To the library.（図書館へ。）

行き先を聞いたあとの自然な返答は、3「Have a nice day.（よい一日を。）」です。
1「It’s late at night.（夜遅いよ。）」・2「I studied science.（科学を勉強したよ。）」はこの場面のあいさつとして弱くなります。
""",
    50: """放送文
M: How was your sister’s birthday?（お姉さんの誕生日はどうだった？）
W: We had a big party.（大きなパーティーをしたよ。）
M: Did she like it?（気に入った？）

気に入ったかへの答えなので、2「Yes. She got many presents.（うん。たくさんプレゼントをもらったよ。）」が自然です。
1「I like chocolate cake.（チョコケーキが好き。）」・3「Thank you for coming.（来てくれてありがとう。）」はこの質問への直接の答えになりません。
""",
}


def _replace_explanations(path: Path, mapping: dict[int, str]) -> int:
    text = path.read_text(encoding='utf-8')
    updated = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal updated
        n = int(match.group(1))
        if n not in mapping:
            return match.group(0)
        updated += 1
        body = mapping[n].rstrip() + '\n'
        return f'【解説{n}】\n{body}'

    # Replace from 【解説N】 through next --- or EOF
    new_text = re.sub(
        r'【解説(\d+)】\n.*?(?=\n---|\Z)',
        repl,
        text,
        flags=re.S,
    )
    path.write_text(new_text, encoding='utf-8')
    return updated


def _dedupe_separators(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    new = re.sub(r'(?:\n---\s*){2,}', '\n\n---\n\n', text)
    if new != text:
        path.write_text(new, encoding='utf-8')
        return True
    return False


def main() -> None:
    files = [
        (_Q / 'listening_conversation_questions.txt', CONVERSATION_EXPL),
        (_Q / 'listening_passage_questions.txt', PASSAGE_EXPL),
        (_Q / 'listening_illustration_questions.txt', ILLUSTRATION_EXPL),
    ]
    for path, mapping in files:
        n = _replace_explanations(path, mapping)
        print(f'{path.name}: updated {n} explanations')

    for name in [
        'grammar_fill_questions.txt',
        'conversation_questions.txt',
        'wordorder_questions.txt',
        'reading_comprehesion_questions.txt',
        'listening_illustration_questions.txt',
        'listening_conversation_questions.txt',
        'listening_passage_questions.txt',
    ]:
        path = _Q / name
        if _dedupe_separators(path):
            print(f'{name}: cleaned double ---')
        else:
            print(f'{name}: no double ---')


if __name__ == '__main__':
    main()
