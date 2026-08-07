#!/usr/bin/env python3
"""
3級 2026①追記分（リスニング41–50）の解説を既存トーンに揃える。

- 放送文に日本語訳（…）を付与
- Question に日本語訳を付与（会話・パッセージ）
- 正解根拠 + 外れ選択肢の短い却下理由

正解番号は build_level3_202601.py の L マップに合わせる
（illustration L[1..10] / conversation L[11..20] / passage L[21..30]）。
"""
from __future__ import annotations

import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_Q = _REPO / 'data' / 'questions' / 'level3'

# (start_q, end_q) inclusive replacements: full 【解説N】... body (without header)
CONVERSATION_EXPL = {
    41: """放送文
M: Did you join the art club again this year, Kathy?（キャシー、今年も美術部に入った？）
W: No. I wanted to try something new, so I joined the dance club.（ううん。新しいことをしたくて、ダンス部に入ったの。）
M: I joined the swimming club.（僕は水泳部に入ったよ。）
W: Sounds like fun.（楽しそう。）
Question: What club is Kathy in this year?（キャシーは今年どの部に入っていますか？）

Kathy が「I joined the dance club（ダンス部に入った）」と明言しているので、2「The dance club.（ダンス部。）」が正解です。
1「The art club.」は今年はやめており、4「The swimming club.」は相手（男性）のクラブ、3「The music club.」は会話に出てきません。
""",
    42: """放送文
M: I don’t want to go to the park. It’s too hot.（公園には行きたくない。暑すぎるよ。）
W: But Sam, we planned to have a picnic!（でもサム、ピクニックの予定だったじゃない！）
M: I’m sorry, but I hate this kind of weather.（ごめん、こういう天気は嫌いなんだ。）
W: OK, let’s stay home.（わかった、家にいよう。）
Question: Why did they decide to stay home?（2人が家にいることにした理由は何ですか？）

Sam が「It’s too hot」「I hate this kind of weather（暑い天気が嫌い）」と言って家にいることにしたので、3「Sam doesn’t like hot days.（サムは暑い日が嫌い。）」が正解です。
1「公園が嫌い」・2「ピクニックが嫌い」ではなく、4「雨の日が嫌い」も会話にありません。
""",
    43: """放送文
M: Hey, Jane, let’s go and get something to eat.（ジェーン、何か食べに行こう。）
W: OK, Bob. Let’s go to the Chinese restaurant on 5th Street. It’s very popular.（いいよ、ボブ。5番街の中華料理店に行こう。とても人気があるの。）
M: Sounds good, but isn’t it expensive?（いいね。でも高くない？）
W: A little, but the food is really good.（少し高いけど、料理は本当においしいよ。）
Question: What does Jane think of the Chinese restaurant?（ジェーンはその中華料理店をどう思っていますか？）

「the food is really good（料理は本当においしい）」と言っているので、3「The food is good.（料理がおいしい。）」が正解です。
1「人気がない」は「very popular」と矛盾、2「高くない」は「A little（少し高い）」と矛盾、4「小さい」は会話に出てきません。
""",
    44: """放送文
M: Let’s go shopping on Saturday afternoon, Betty.（ベティ、土曜の午後に買い物に行こう。）
W: I’d love to, but I have to work.（行きたいけど、仕事があるの。）
M: How about Sunday before lunch, then?（じゃあ日曜の昼食前はどう？）
W: Sure. Let’s meet at the station at ten.（いいよ。駅で10時に会おう。）
Question: When will they meet?（2人はいつ会いますか？）

日曜の昼食前・駅で10時に会うので、3「Sunday morning.（日曜の朝。）」が正解です。
1・2の土曜は仕事で行けず、4「Sunday afternoon」は昼食前ではないので合いません。
""",
    45: """放送文
M: Where were you this morning? We had a science club meeting.（今朝どこにいたの？科学クラブの会合があったよ。）
W: Really?（え、そうなの？）
M: Yes. Mr. Burns told us about it yesterday.（うん。バーンズ先生が昨日教えてくれたよ。）
W: I wasn’t at school yesterday.（昨日は学校にいなかったの。）
Question: What happened to the girl this morning?（女の子は今朝どうなりましたか？）

今朝の科学クラブの会合にいなかったので、1「She missed a meeting.（会合を欠席した。）」が正解です。
2「バーンズ先生を見つけられなかった」・3「レポートをなくした」・4「テストに遅れた」は会話に出てきません。
""",
    46: """放送文
W: Ken, why aren’t you at school?（ケン、どうして学校にいないの？）
M: Sorry, Mom. I woke up late this morning.（ごめん、お母さん。今朝起き遅れたんだ。）
W: I am very angry. Please go after breakfast.（とても怒っているわ。朝食のあと行きなさい。）
M: OK.（わかった。）
Question: Why is Ken’s mother angry?（ケンのお母さんはなぜ怒っていますか？）

まだ学校へ行っていない（起き遅れた）ことに怒っているので、4「Ken has not left for school.（ケンがまだ学校へ出ていない。）」が正解です。
1「朝食を作らなかった」・2「早く帰ってこなかった」・3「部屋を掃除していない」は会話の怒りの理由ではありません。
""",
    47: """放送文
W: I’m reading a book about science.（科学の本を読んでいるの。）
M: That sounds interesting. I want to read about history.（おもしろそう。僕は歴史について読みたいな。）
W: You should read this mystery book.（このミステリーの本を読むといいよ。）
M: OK, I’ll borrow that instead.（わかった。じゃあそれを借りるよ。）
Question: Which book will the boy borrow?（男の子はどの本を借りますか？）

「I’ll borrow that instead」の that は mystery book なので、3「A mystery book.（ミステリーの本。）」が正解です。
1「A history book.」は読みたいと思っていただけ、4「A science book.」は女性が読んでいる本、2「A math book.」は会話に出てきません。
""",
    48: """放送文
W: Tom, do you want to play soccer after school?（トム、放課後サッカーしない？）
M: Sorry, I can’t. I’m going to the park with my cousin.（ごめん、できない。いとこといっしょに公園へ行くんだ。）
W: Oh, I see. Well, have fun.（ああ、そうなんだ。じゃあ楽しんでね。）
M: Thanks.（ありがとう。）
Question: Who is Tom going to the park with?（トムは誰と公園へ行きますか？）

「with my cousin（いとこと）」とあるので、3「His cousin.（彼のいとこ。）」が正解です。
1「友達」・2「両親」・4「妹」は会話に出てきません。
""",
    49: """放送文
M: Is this blue book yours, Sarah?（サラ、この青い本は君の？）
W: No, mine has a green cover. I think it is Ken’s.（ううん、私のは緑の表紙。ケンの本だと思う。）
M: No, his book is yellow.（いや、彼の本は黄色だよ。）
W: Then, it is probably Emily’s. Let’s ask her later.（じゃあ、たぶんエミリーのね。あとで聞いてみよう。）
Question: Which book is Sarah’s?（サラの本はどれですか？）

Sarah 本人が「mine has a green cover（私のは緑の表紙）」と言っているので、1「The one with a green cover.（緑の表紙の本。）」が正解です。
3の青い本は今見ている本、4の黄色は Ken の本、2の赤い表紙は会話に出てきません。
""",
    50: """放送文
W: What do you like to do in your free time, Mark?（マーク、暇なときは何をするのが好き？）
M: I love painting. How about you?（絵を描くのが大好き。君は？）
W: I play the guitar and write songs.（ギターを弾いて曲を書くよ。）
M: That’s cool.（かっこいいね。）
Question: What does Mark do in his free time?（マークは暇なときに何をしますか？）

Mark が「I love painting（絵を描くのが大好き）」と言っているので、1「He paints.（絵を描く。）」が正解です。
2「曲を書く」・3「ギターを弾く」は相手（女性）の趣味、4「歌う」は会話に出てきません。
""",
}

PASSAGE_EXPL = {
    41: """放送文
W: My mom is an elementary school teacher, and my dad teaches science at a high school. My friends think I’ll become a teacher, too, but I want to be a famous violinist.（お母さんは小学校の先生で、お父さんは高校で理科を教えています。友達は私も先生になると思っているけど、私は有名なバイオリニストになりたいです。）
Question: What does the girl want to be?（女の子は何になりたいですか？）

「I want to be a famous violinist（有名なバイオリニストになりたい）」とあるので、1「A famous musician.（有名な音楽家。）」が正解です。
2・3の教師は親の職業や友人の予想、4「科学者」は話に出てきません。
""",
    42: """放送文
M: Amy works five days a week, but next year, she’ll only work three. She wants to spend more time with her son. He’s only two years old.（エイミーは週5日働いていますが、来年は週3日だけになります。2歳の息子ともっと過ごしたいからです。）
Question: How many days a week does Amy work now?（エイミーは今、週に何日働いていますか？）

今は「five days a week」なので、4「Five.（5日。）」が正解です。
3「Three.」は来年の予定、1・2は話に出てきません。
""",
    43: """放送文
M: Rick wants money to buy a new bike. He wanted to work at his favorite restaurant, but the restaurant didn’t need any help. So he got a job at a supermarket. He’ll start next week.（リックは新しい自転車を買うお金がほしいです。好きなレストランで働きたかったのですが、人手は要りませんでした。それでスーパーで仕事を見つけ、来週から始めます。）
Question: How will Rick get money to buy a bike?（リックはどうやって自転車を買うお金を得ますか？）

「he got a job at a supermarket（スーパーで仕事を得た）」ので、1「He’ll work at a supermarket.（スーパーで働く。）」が正解です。
3「レストランで働く」は採用されず、2・4の親や祖父母に頼む話はありません。
""",
    44: """放送文
M: Mark wasn’t feeling well in school today and wanted to go home. His teacher called Mark’s mother. Mark’s mother came to school and took him to the doctor.（マークは今日学校で気分が悪く、家に帰りたがりました。先生が母親に電話し、母親が学校へ来て医者に連れていきました。）
Question: What did Mark’s teacher do?（マークの先生は何をしましたか？）

先生がしたのは「called Mark’s mother（母親に電話した）」ことなので、1「She called Mark’s mother.（マークの母親に電話した。）」が正解です。
2「家へ連れて帰った」・3「医者に連れていった」は母親、4「薬をあげた」は話に出てきません。
""",
    45: """放送文
W: I’m going to an important event, so I need some nice clothes. I already have nice shoes, but I need to get a new skirt. I’ll also wear the watch my brother gave me.（大事な行事に行くので、きれいな服が必要です。すてきな靴はもうあるけど、新しいスカートが要ります。兄がくれた腕時計もします。）
Question: What will the woman buy for the event?（女性は行事のために何を買いますか？）

「I need to get a new skirt（新しいスカートが要る）」ので、4「A skirt.（スカート。）」が正解です。
2「靴」はすでにあり、3「腕時計」は兄からもらったもの、1「手袋」は話に出てきません。
""",
    46: """放送文
M: I usually make breakfast for my family. Today, I got up late, so my father made breakfast. He made pancakes for my brother and me. They were delicious.（普段は家族の朝食を作ります。今日は起き遅れたので、お父さんが朝食を作りました。弟と私のためにパンケーキを作ってくれ、おいしかったです。）
Question: Who made breakfast today?（今日朝食を作ったのは誰ですか？）

「my father made breakfast（お父さんが朝食を作った）」ので、1「The boy’s father.（少年の父親。）」が正解です。
4「少年本人」は普段作る人、2「母親」・3「弟」は話に出てきません（弟は食べた相手です）。
""",
    47: """放送文
W: My brother is a college student. He gets up at seven, eats breakfast for half an hour, and leaves home at eight. He starts his classes at nine and studies until six.（兄は大学生です。7時に起き、30分朝食を食べ、8時に家を出ます。授業は9時に始まり、6時まで勉強します。）
Question: What time does the woman’s brother leave home?（女性の兄は何時に家を出ますか？）

「leaves home at eight（8時に家を出る）」ので、3「At 8:00.（8時。）」が正解です。
1「7:00」は起床、4「9:00」は授業開始、2「7:30」は話に出てきません。
""",
    48: """放送文
W: Thank you for coming to our restaurant. Today’s special is chicken curry. It comes with fresh bread. The cook is making it in the kitchen now. Enjoy your meal.（当店へお越しいただきありがとうございます。本日の特別メニューはチキンカレーです。新鮮なパンが付きます。今、厨房でコックが作っています。どうぞお召し上がりください。）
Question: Where is the woman talking?（女性はどこで話していますか？）

「Thank you for coming to our restaurant（レストランへお越しいただきありがとう）」と言っているので、2「In a restaurant.（レストランで。）」が正解です。
1「スーパー」・3「図書館」・4「駅」は話の場面ではありません。
""",
    49: """放送文
M: John went to the supermarket yesterday. He wanted to buy some chocolate, but the supermarket did not have any. He bought some apples and a bottle of orange juice instead.（ジョンは昨日スーパーへ行きました。チョコレートを買いたかったのですが、ありませんでした。代わりにりんごとオレンジジュースを買いました。）
Question: What did John want to buy?（ジョンは何を買いたかったですか？）

「He wanted to buy some chocolate（チョコレートを買いたかった）」ので、2「Some chocolate.（チョコレート。）」が正解です。
1「りんご」・4「ジュース」は代わりに買ったもの、3「オレンジ」は話に出てきません（オレンジジュースです）。
""",
    50: """放送文
W: There was a big festival in my town last weekend. I went with my sister, and I met some of my friends there. I was happy to see them.（先週末、私の町で大きなフェスティバルがありました。妹といっしょに行き、そこで友達に会いました。会えてうれしかったです。）
Question: Where did the woman go last weekend?（女性は先週末どこへ行きましたか？）

「a big festival in my town」に行ったので、4「To a festival.（フェスティバルへ。）」が正解です。
1「妹の家」は同行者の話、3「友達の家」はそこで会った相手、2「美術館」は話に出てきません。
""",
}

ILLUSTRATION_EXPL = {
    41: """放送文
M: What is a popular book for young children?（小さな子どもに人気の本は何？）
W: Here is a good one.（これ、いい本よ。）
M: What kind of book is it?（どんな種類の本？）

本の種類を聞いているので、1「It’s science fiction.（SFです。）」が自然です。
2「I read it at school.（学校で読んだよ。）」はいつ読んだか、3「They like animals.（彼らは動物が好き。）」は好きなものの話で、種類の答えになりません。
""",
    42: """放送文
M: Do you still have my history textbook?（まだ僕の歴史の教科書持ってる？）
W: Yes, Scott.（うん、スコット。）
M: Well, I’ll need it next week.（来週それが必要なんだ。）

来週必要と言っているので、返す約束の1「I can bring it tomorrow.（明日持っていけるよ。）」が自然です。
2「I hope you can buy it.（買ってくれるといいな。）」・3「I’ll take a look.（見てみるね。）」では「持っている」前提の流れに合いにくいです。
""",
    43: """放送文
M: You need to clean your room, Jane.（ジェーン、部屋を掃除しなきゃ。）
W: I’ll do it tomorrow.（明日やるよ。）
M: Why can’t you do it today?（どうして今日はできないの？）

今日できない理由を聞いているので、2「I have to study for a test.（テスト勉強しなきゃ。）」が自然です。
1「It’s in the living room.（リビングにあるよ。）」は場所、3「Thanks for helping me.（手伝ってくれてありがとう。）」はお礼で、理由の答えになりません。
""",
    44: """放送文
M: Here’s your steak. Would you like anything else?（ステーキです。ほかにご注文は？）
W: No, thanks.（いいえ、結構です。）
M: OK. Enjoy your meal.（わかりました。どうぞお召し上がりください。）

「楽しんで」への返事なので、2「I’m sure I will.（きっとそうするよ。）」が自然です。
1「Yes, that’s fine.（ええ、それでいいよ。）」・3「Just one, please.（1つだけで。）」はこの締めのあいさつへの応答として弱くなります。
""",
    45: """放送文
M: When are you going on vacation, Marge?（マージ、いつ休暇に行くの？）
W: In two weeks.（2週間後よ。）
M: Where will you go?（どこへ行くの？）

行き先を聞いているので、1「To a beach in Thailand.（タイのビーチへ。）」が自然です。
2「Two or three of them, please.（2つか3つください。）」は個数、3「To my Spanish class.（スペイン語の授業へ。）」は行き先の答えとして合いません。
""",
    46: """放送文
W: What’s your favorite subject?（好きな科目は何？）
M: I love studying English.（英語の勉強が大好き。）
W: How often do you study?（どのくらいの頻度で勉強するの？）

頻度を聞いているので、2「For one hour every afternoon.（毎午後1時間。）」が自然です。
1「After two months.（2か月後。）」や 3「I went to America last year.（去年アメリカへ行った。）」は頻度の答えになりません。
""",
    47: """放送文
M: Excuse me. Does this train stop at Green Hills?（すみません。この電車はグリーンヒルズに停まりますか？）
W: Yes. I get off there, too.（はい。私もそこで降ります。）
M: That’s good to know. Thanks.（そうですか、助かります。ありがとう。）

お礼への定番の返事は、3「It’s my pleasure.（どういたしまして。）」です。
1「I don’t take a train.（電車には乗らないよ。）」・2「It’s big.（大きいよ。）」はこのやりとりに合いません。
""",
    48: """放送文
M: Has Naomi found her book?（ナオミは本を見つけた？）
W: No, she still hasn’t.（ううん、まだだよ。）
M: Did she check the classroom?（教室は調べた？）

教室を調べたかへの答えなので、見つからなかった1「She couldn’t find it there.（そこでは見つからなかったよ。）」が自然です。
2「It was in her bag.（かばんの中にあったよ。）」・3「The teacher gave it to her.（先生が渡したよ。）」は「まだ見つかっていない」という直前の話と矛盾しやすいです。
""",
    49: """放送文
W: Tom, your shoes are old.（トム、その靴は古いわね。）
M: I know. I’ve used them for two years.（わかってる。2年使ってるんだ。）
W: I can even see a hole.（穴まで見えるわ。）

穴が空いていると言われたあとの反応なので、3「Oh, I’ll get new ones.（あ、新しいのを買うよ。）」が自然です。
1「You went to the department store.（デパートに行ったね。）」・2「Your socks are very pretty.（その靴下、とてもきれいね。）」では穴への応答になりません。
""",
    50: """放送文
M: I want to go to the library.（図書館へ行きたいな。）
W: It’s going to rain soon.（もうすぐ雨が降りそうよ。）
M: But I wanted to ride my bike there.（でも自転車で行きたかったんだ。）

雨なのに自転車で行こうとしているので、2「That’s not a good idea.（それはいい考えじゃないよ。）」が自然です。
1「Wait until it stops snowing.（雪がやむまで待ちなさい。）」は雪の話、3「I went for a walk.（散歩に行ったよ。）」はこの助言としてずれます。
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
    total = 0
    for path, mapping in files:
        n = _replace_explanations(path, mapping)
        total += n
        print(f'{path.name}: updated {n} explanations')
    print(f'Total explanations updated: {total}')

    for path in sorted(_Q.glob('*.txt')):
        if _dedupe_separators(path):
            print(f'{path.name}: cleaned double ---')
        else:
            print(f'{path.name}: no double ---')


if __name__ == '__main__':
    main()
