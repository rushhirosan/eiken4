from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import random

class Command(BaseCommand):
    help = 'Creates grammar fill-in-the-blank questions with explanations'

    def handle(self, *args, **options):
        # 問題のテンプレート
        questions = [
            {
                'text': 'A: Did you () the speech contest, Mika? B: Yes, I did. I\'m happy.',
                'correct_answer': 'win',
                'wrong_answers': ['walk', 'fall', 'ride'],
                'explanation': '「win」は「勝つ」という意味です。Mikaはスピーチコンテストに出て、「Yes, I did. I\'m happy.」と言っています。「happy（うれしい）」になる理由は、コンテストに勝ったからだと考えるのが自然です。他の選択肢「walk（歩く）」「fall（落ちる）」「ride（乗る）」はコンテストの結果には関係ないので不適切です。'
            },
            {
                'text': 'A: Why is Maria () with you? B: I don\'t know. She isn\'t talking to me.',
                'correct_answer': 'angry',
                'wrong_answers': ['delicious', 'fast', 'thin'],
                'explanation': '「angry」は「怒っている」という意味です。Mariaが「話してくれない」という状況から、「怒っている」と推測できます。他の選択肢「delicious（おいしい）」「fast（速い）」「thin（やせている）」は、人の感情や態度とは関係がないので不正解です。'
            },
            {
                'text': 'Josh went to an art () yesterday. He saw a lot of interesting paintings there.',
                'correct_answer': 'museum',
                'wrong_answers': ['pencil', 'question', 'color'],
                'explanation': '「museum」は「博物館、美術館」という意味です。art（芸術）に関係があり、たくさんのpainting（絵）を展示している場所は「museum（美術館）」です。「pencil（えんぴつ）」「question（質問）」「color（色）」は場所ではないので合いません。'
            },
            {
                'text': 'A: What\'s wrong, Hana? B: I\'m (). I want to go to bed.',
                'correct_answer': 'sleepy',
                'wrong_answers': ['loud', 'long', 'snowy'],
                'explanation': '「sleepy」は「眠い」という意味です。「go to bed（寝に行く）」と言っているので、眠い(sleepy)と考えるのが自然です。他の選択肢「loud（うるさい）」「long（長い）」「snowy（雪の降る）」は体の状態を表す言葉ではないので不正解です。'
            },
            {
                'text': 'Larry lives in a big city, but he wants to move to a small () in the future.',
                'correct_answer': 'town',
                'wrong_answers': ['flower', 'book', 'cup'],
                'explanation': '「town」は「町」という意味です。「big city（大きな都市）」に住んでいるけれど、将来は「small town（小さな町）」に住みたいと言っているので、「town」が自然です。「flower（花）」「book（本）」「cup（カップ）」は場所を表さないので間違いです。'
            },
            {
                'text': 'A: Are you () for the test, Lisa? B: Yes, I am. I studied a lot yesterday.',
                'correct_answer': 'ready',
                'wrong_answers': ['heavy', 'noisy', 'true'],
                'explanation': '「ready」は「準備ができた」という意味です。Lisaは「たくさん勉強した」と言っているので、「テストの準備ができている」という意味になります。他の選択肢「heavy（重い）」「noisy（うるさい）」「true（本当の）」は文脈に合いません。'
            },
            {
                'text': 'Yumi is a high school teacher in Japan. Her () is a college student in America.',
                'correct_answer': 'daughter',
                'wrong_answers': ['cloud', 'pie', 'money'],
                'explanation': '「daughter」は「娘」という意味です。「彼女の娘がアメリカの大学生」という文脈です。他の選択肢「cloud（雲）」「pie（パイ）」「money（お金）」は人を表さないので不自然です。'
            },
            {
                'text': 'A: Did your brother help you with your homework? B: Yes. He\'s always very () to me.',
                'correct_answer': 'kind',
                'wrong_answers': ['tall', 'slow', 'wet'],
                'explanation': '「kind」は「親切な」という意味です。「助けてくれた」ということなので、「親切な(kind)」がぴったりです。「tall（背が高い）」「slow（遅い）」「wet（ぬれている）」は、性格を表す形容詞ではないので合いません。'
            },
            {
                'text': 'Tony loves to travel. In the future, he wants to travel all over the ().',
                'correct_answer': 'world',
                'wrong_answers': ['ear', 'box', 'arm'],
                'explanation': '「world」は「世界」という意味です。「将来、世界中を旅行したい」と言っているので「world」が正解です。「ear（耳）」「box（箱）」「arm（腕）」では意味が通じません。'
            },
            {
                'text': 'Luke is good () playing tennis. He is on the school team.',
                'correct_answer': 'at',
                'wrong_answers': ['of', 'up', 'to'],
                'explanation': '「be good at ～」は「～が得意」という意味の決まった表現です。テニスが得意だから学校のチームに入っている、という流れになります。前置詞を正しく覚えましょう！'
            },
            {
                'text': 'A: Can I use your computer now? B: () a minute. I need to read an e-mail first.',
                'correct_answer': 'Wait',
                'wrong_answers': ['Fall', 'Cut', 'Put'],
                'explanation': '「Wait a minute.」は「ちょっと待って」という定番表現です。「Fall（落ちる）」「Cut（切る）」「Put（置く）」はこの場面では使いません。'
            },
            {
                'text': 'A: You can\'t go to bed now. () a bath first. B: OK, Mom.',
                'correct_answer': 'Take',
                'wrong_answers': ['Drive', 'Wear', 'Send'],
                'explanation': '「take a bath」は「お風呂に入る」という意味の決まり文句です。英語では「take」を使うことを覚えましょう。「Drive（運転する）」「Wear（着る）」「Send（送る）」では意味が通じません。'
            },
            {
                'text': 'A: There () many interesting animals at this zoo. B: Yes. I want to come here again.',
                'correct_answer': 'are',
                'wrong_answers': ['is', 'am', 'be'],
                'explanation': '「animals」と複数形なので、「are」を使います。「There are ～」で「～がある、いる」という意味になります。「is」は単数形に使うので、ここでは不正解です。'
            },
            {
                'text': 'A: Is skiing () than snowboarding, Tom? B: I think so, but it\'s a lot of fun.',
                'correct_answer': 'harder',
                'wrong_answers': ['hard', 'hardest', 'too hard'],
                'explanation': '「than」があるので、比較級を使うことがわかります。「hard」の比較級は「harder」。「hard」は原形、「hardest」は最上級、「too hard」は「難しすぎる」という意味なので文脈に合いません。'
            },
            {
                'text': 'A: Did you get any food at the baseball stadium yesterday, Linda? B: Yes. I () two hot dogs. They were delicious.',
                'correct_answer': 'ate',
                'wrong_answers': ['eat', 'eating', 'eats'],
                'explanation': '「did」という過去形の質問なので、答えも過去形で答える必要があります。「ate」は「eat（食べる）」の過去形です。他の選択肢は形が合わないので不正解です。'
            },
            {
                'text': 'A: Do you like cats () dogs? B: I like cats better.',
                'correct_answer': 'or',
                'wrong_answers': ['and', 'so', 'but'],
                'explanation': '「or」は「または、あるいは」という意味です。ここでは「猫が好きですか、犬が好きですか」という選択肢を提示しているので、「or」が自然です。「and（そして）」「so（だから）」「but（しかし）」はこの文脈には合いません。'
            },
            {
                'text': 'A: Your jacket is very nice. B: Thank you. It was a () from my mother.',
                'correct_answer': 'gift',
                'wrong_answers': ['call', 'store', 'game'],
                'explanation': '「gift」は「贈り物、プレゼント」という意味です。母からもらったものなので「gift」がぴったりです。「call（呼ぶ）」「store（店）」「game（ゲーム）」はここでは意味が通じません。'
            },
            {
                'text': 'A: Are you going to the party () Saturday? B: Yes, I am.',
                'correct_answer': 'on',
                'wrong_answers': ['in', 'at', 'to'],
                'explanation': '曜日（Saturday）の前には「on」を使います。英語では、日や曜日の前には「on」、月や年の前には「in」を使うのが基本ルールです。「at」は場所や時刻、「to」は方向なのでここでは使いません。'
            },
            {
                'text': 'A: We are going to () the school festival next week. B: I\'m excited!',
                'correct_answer': 'have',
                'wrong_answers': ['give', 'stand', 'bring'],
                'explanation': '「have a festival」で「祭りを開催する」という意味になります。イベントを「持つ＝開催する」という感覚です。「give（与える）」「stand（立つ）」「bring（持ってくる）」は意味がずれます。'
            },
            {
                'text': 'A: What is Ken doing now? B: He is () a book in his room.',
                'correct_answer': 'reading',
                'wrong_answers': ['reading at', 'read', 'reads'],
                'explanation': '「be動詞＋動詞-ing」で現在進行形を作ります。Kenが「今」している動作なので「reading」が正解です。「read」は原形、「reads」は三人称単数現在、「reading at」は文法的におかしいです。'
            },
            {
                'text': 'A: Where is Dad? B: He\'s () dinner in the kitchen.',
                'correct_answer': 'making',
                'wrong_answers': ['walking', 'playing', 'cutting'],
                'explanation': '「make dinner」で「夕食を作る」という意味になります。料理をする場面なので「make」が自然です。「walk（歩く）」「play（遊ぶ）」「cut（切る）」は合いません。'
            },
            {
                'text': 'A: What\'s your favorite () ? B: I like soccer.',
                'correct_answer': 'sport',
                'wrong_answers': ['food', 'book', 'color'],
                'explanation': '「soccer（サッカー）」はスポーツの一種なので、「favorite sport（お気に入りのスポーツ）」が正しいです。「food（食べ物）」「book（本）」「color（色）」では話が合いません。'
            },
            {
                'text': 'A: Let\'s () to the park this afternoon. B: Good idea!',
                'correct_answer': 'go',
                'wrong_answers': ['take', 'make', 'run'],
                'explanation': '「Let\'s go to ～」は「～へ行こう」という誘い文句でよく使います。「take（持っていく）」「make（作る）」「run（走る）」はここでは意味が通じません。'
            },
            {
                'text': 'A: Is this your pencil? B: No, it\'s () .',
                'correct_answer': 'mine',
                'wrong_answers': ['my', 'me', 'I'],
                'explanation': '「mine」は「私のもの」という意味の所有代名詞です。「It is mine.（それは私のものです）」という形が自然です。「my」は形容詞なので後ろに名詞が必要、「me（私を）」「I（私は）」は主語なので違います。'
            },
            {
                'text': 'A: Look at those clouds! B: It\'s going to () soon.',
                'correct_answer': 'snow',
                'wrong_answers': ['swim', 'teach', 'cook'],
                'explanation': '雲がたくさんある→天気の変化→「snow（雪が降る）」を予想している流れです。「swim（泳ぐ）」「teach（教える）」「cook（料理する）」では天気の話に合いません。'
            },
            {
                'text': 'A: How () oranges are there? B: Five.',
                'correct_answer': 'many',
                'wrong_answers': ['much', 'long', 'big'],
                'explanation': '数えられるもの（oranges：オレンジ）には「many」を使います。「How many ～?（いくつの～？）」が正しい聞き方です。「much」は数えられないもの（水や砂など）に使うので不正解です。'
            },
            {
                'text': 'A: I have a () tomorrow. B: Good luck!',
                'correct_answer': 'test',
                'wrong_answers': ['camera', 'present', 'country'],
                'explanation': '「Good luck!（頑張って！）」という返事から、「test（テスト）」であることがわかります。「camera（カメラ）」「present（プレゼント）」「country（国）」は状況に合いません。'
            },
            {
                'text': 'A: Can you () me your notebook? B: Sure, here you are.',
                'correct_answer': 'show',
                'wrong_answers': ['clean', 'take', 'jump'],
                'explanation': '「show」は「見せる」という意味です。ノートを見せてほしいというお願いなので「show」が正しいです。「clean（掃除する）」「take（取る）」「jump（跳ぶ）」は不自然です。'
            },
            {
                'text': 'A: Whose bag is this? B: It\'s () .',
                'correct_answer': 'Amy\'s',
                'wrong_answers': ['Amy', 'Amys', 'Amy is'],
                'explanation': '所有を表すときは、「\'s」をつけます。「Amy\'s bag（エイミーのバッグ）」の省略で「It\'s Amy\'s.」となっています。「Amy（名前だけ）」「Amys（間違った複数形）」「Amy is（エイミーは）」は不自然です。'
            },
            {
                'text': 'A: What time do you () up? B: I usually get up at 7 a.m.',
                'correct_answer': 'get',
                'wrong_answers': ['bring', 'wake', 'give'],
                'explanation': '「get up」は「起きる」という意味の決まり文句です。「wake up」も似た意味ですが、ここは「get up」を使うのが自然です。「bring（持ってくる）」「give（与える）」では意味が通じません。'
            },
            {
                'text': 'A: Did you () the library yesterday? B: Yes, I borrowed some books.',
                'correct_answer': 'visit',
                'wrong_answers': ['play', 'cook', 'open'],
                'explanation': '「visit」は「訪れる」という意味です。図書館に行って本を借りた、という流れなので「visit」が正解です。「play（遊ぶ）」「cook（料理する）」「open（開ける）」では合いません。'
            },
            {
                'text': 'A: Where does your brother work? B: He works in a big () .',
                'correct_answer': 'office',
                'wrong_answers': ['sea', 'garden', 'farm'],
                'explanation': '「office（オフィス）」は働く場所を表します。「sea（海）」「garden（庭）」「farm（農場）」も場所ですが、「big office」が一番自然な流れです。'
            },
            {
                'text': 'A: Excuse me. How () is it to the station? B: About ten minutes on foot.',
                'correct_answer': 'far',
                'wrong_answers': ['many', 'long', 'much'],
                'explanation': '距離をたずねるときは「How far（どれくらい遠い）」を使います。「long」は時間の長さ、「much」「many」は量や数に使うので違います。'
            },
            {
                'text': 'A: I can\'t () the answer. B: Let\'s ask the teacher.',
                'correct_answer': 'find',
                'wrong_answers': ['listen', 'hold', 'clean'],
                'explanation': '「find」は「見つける」という意味です。「答えが見つからない」という話なので「find」がぴったりです。「listen（聞く）」「hold（持つ）」「clean（掃除する）」は意味が合いません。'
            },
            {
                'text': 'A: How\'s the weather today? B: It\'s very () . Let\'s stay inside.',
                'correct_answer': 'rainy',
                'wrong_answers': ['sunny', 'funny', 'tasty'],
                'explanation': '「stay inside（家の中にいよう）」という流れなので、外に出たくない天気、「rainy（雨の）」がぴったりです。「sunny（晴れ）」だったら外に出たくなるはず。「funny（おもしろい）」「tasty（おいしい）」は天気には使いません。'
            },
            {
                'text': 'A: How often do you () your grandparents? B: About once a month.',
                'correct_answer': 'visit',
                'wrong_answers': ['watch', 'listen', 'catch'],
                'explanation': '「visit」は「訪問する」という意味です。おじいちゃんおばあちゃんに会いに行く、という意味にぴったりです。「watch（見る）」「listen（聞く）」「catch（捕まえる）」はここでは不自然です。'
            },
            {
                'text': 'A: I can\'t find my keys. B: Look () your bag again.',
                'correct_answer': 'for',
                'wrong_answers': ['at', 'on', 'in'],
                'explanation': '「look for」は「探す」という意味の熟語です。鍵が見つからないので「探して」という意味になります。「look at（見る）」では意味が違います。'
            },
            {
                'text': 'A: Could you () the door, please? B: Sure!',
                'correct_answer': 'open',
                'wrong_answers': ['drink', 'paint', 'grow'],
                'explanation': '「open the door」で「ドアを開ける」という意味です。「drink（飲む）」「paint（塗る）」「grow（育てる）」はドアに使う動詞ではありません。'
            },
            {
                'text': 'A: How was the movie? B: It was () than I thought.',
                'correct_answer': 'better',
                'wrong_answers': ['good', 'best', 'well'],
                'explanation': '「than（～より）」があるので比較級を使います。「better」は「good」の比較級です。「good（原形）」「best（最上級）」「well（上手に）」は文法的に合いません。'
            },
            {
                'text': 'A: May I borrow your dictionary? B: Of () . Here you are.',
                'correct_answer': 'course',
                'wrong_answers': ['self', 'way', 'sure'],
                'explanation': '「Of course.（もちろん）」は、お願いを快く受け入れるときによく使う表現です。「self（自己）」「way（道）」「sure（確信して）」は文脈に合いません。'
            },
            {
                'text': 'A: You look tired. B: I stayed up () last night to finish my homework.',
                'correct_answer': 'late',
                'wrong_answers': ['slowly', 'strongly', 'badly'],
                'explanation': '「stay up late」で「夜遅くまで起きている」という意味です。「slowly（ゆっくり）」「strongly（強く）」「badly（ひどく）」は違います。'
            },
            {
                'text': 'A: My sister () to Italy last summer. B: Wow, sounds exciting!',
                'correct_answer': 'went',
                'wrong_answers': ['goes', 'go', 'going'],
                'explanation': '「last summer（去年の夏）」とあるので、過去形「went」を使います。「go（原形）」「goes（三人称単数現在）」「going（進行形）」はここでは使えません。'
            },
            {
                'text': 'A: When did you () studying French? B: Two years ago.',
                'correct_answer': 'begin',
                'wrong_answers': ['began', 'begins', 'beginning'],
                'explanation': '「did」があるので後ろは動詞の原形を使います。「begin（始める）」が正解です。「began（過去形）」「begins（三人称単数現在）」「beginning（進行形）」はダメです。'
            },
            {
                'text': 'A: This bag is too heavy. B: I\'ll () you carry it.',
                'correct_answer': 'help',
                'wrong_answers': ['let', 'call', 'tell'],
                'explanation': '「help 人 動詞」で「～するのを手伝う」という形です。「carry it（それを運ぶ）」の手伝いを申し出ているので「help」がぴったりです。「let（許す）」「call（呼ぶ）」「tell（言う）」は不自然です。'
            },
            {
                'text': 'A: What will you do this weekend? B: I () to the beach with my family.',
                'correct_answer': 'will go',
                'wrong_answers': ['went', 'goes', 'going'],
                'explanation': '「this weekend（今週末）」について話しているので未来の話です。「will＋動詞の原形」で未来を表します。「went（過去形）」「goes（三人称単数現在）」「going（進行形）」では合いません。'
            },
            {
                'text': 'A: I have never () to another country. B: I hope you can go someday!',
                'correct_answer': 'traveled',
                'wrong_answers': ['travel', 'traveling', 'travels'],
                'explanation': '「have never＋過去分詞」で「一度も～したことがない」という現在完了形です。「traveled（travelの過去分詞）」を使うのが正しいです。'
            },
            {
                'text': 'A: Which do you like () , spring or summer? B: I like spring.',
                'correct_answer': 'better',
                'wrong_answers': ['best', 'good', 'well'],
                'explanation': '二つを比べてどちらが好きか聞くときは「better」を使います。「best（最も良い）」は三つ以上の比較で使います。'
            },
            {
                'text': 'A: Who is the girl () to your brother? B: Oh, that\'s his classmate.',
                'correct_answer': 'standing',
                'wrong_answers': ['stand', 'stood', 'stands'],
                'explanation': '今兄のそばに「立っている」女の子を表しているので、現在進行の「standing」が正しいです。「stand（立つ）」「stood（立った：過去形）」「stands（三人称単数現在）」では自然な文になりません。'
            },
            {
                'text': 'A: It\'s raining. Let\'s stay inside. B: I agree. We can () a movie at home.',
                'correct_answer': 'watch',
                'wrong_answers': ['see', 'look', 'view'],
                'explanation': '「watch a movie」で「映画を見る」という自然な英語表現です。「see」は「見る」ですが、映画をじっくり見る場合は「watch」を使います。'
            },
            {
                'text': 'A: I don\'t understand this question. B: Why don\'t you ask the () ?',
                'correct_answer': 'teacher',
                'wrong_answers': ['brother', 'student', 'doctor'],
                'explanation': '「わからない質問」があるときは、当然「teacher（先生）」に聞くのが自然です。「brother（兄弟）」「student（生徒）」「doctor（医者）」ではおかしいです。'
            }
        ]

        # 既存の問題を削除
        Question.objects.filter(question_type='grammar_fill', level=4).delete()

        # 問題を作成
        for i, q in enumerate(questions, 1):
            # 選択肢を問題の順序通りに配置
            all_answers = [q['correct_answer']] + q['wrong_answers']
            
            # 問題を作成
            question = Question.objects.create(
                question_type='grammar_fill',
                level=4,
                question_text=q['text'],
                explanation=q['explanation']
            )
            
            # 選択肢を作成（順序を保持）
            for order, answer in enumerate(all_answers, 1):
                Choice.objects.create(
                    question=question,
                    choice_text=answer,
                    is_correct=(answer == q['correct_answer']),
                    order=order
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created question {i}: {q["text"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully created 50 grammar fill-in-the-blank questions with explanations')) 