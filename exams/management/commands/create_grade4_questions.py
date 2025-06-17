from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import random

class Command(BaseCommand):
    help = 'Creates 30 questions for each category of Eiken Grade 4'

    def handle(self, *args, **options):
        """コマンド実行時の処理"""
        level = 4  # 4級用の問題を作成
        
        # 文法問題を作成
        grammar_questions = self._create_grammar_questions()
        self._create_questions(level, 'grammar_fill', 10, grammar_questions)

        # 他の問題形式はコメントアウト
        # conversation_questions = self._create_conversation_questions()
        # self._create_questions(level, 'conversation_fill', 10, conversation_questions)

        # word_order_questions = self._create_word_order_questions()
        # self._create_questions(level, 'word_order', 10, word_order_questions)

        # reading_questions = self._create_reading_questions()
        # self._create_questions(level, 'reading_comprehension', 10, reading_questions)

        # listening_response_questions = self._create_listening_response_questions()
        # self._create_questions(level, 'listening_response', 10, listening_response_questions)

        # listening_conversation_questions = self._create_listening_conversation_questions()
        # self._create_questions(level, 'listening_conversation', 10, listening_conversation_questions)

        # listening_short_passage_questions = self._create_listening_short_passage_questions()
        # self._create_questions(level, 'listening_short_passage', 10, listening_short_passage_questions)

        # listening_illustration_questions = self._create_listening_illustration_questions()
        # self._create_questions(level, 'listening_illustration', 10, listening_illustration_questions)
        
        self.stdout.write(self.style.SUCCESS('文法問題の作成が完了しました。'))

    def _create_questions(self, level, question_type, num_questions, question_list):
        """指定された数の問題を作成"""
        created_count = 0
        existing_questions = set(Question.objects.filter(
            level=level,
            question_type=question_type
        ).values_list('question_text', flat=True))
        
        # 問題リストをシャッフルしてランダムに選択
        random.shuffle(question_list)
        
        for question_data in question_list:
            if created_count >= num_questions:
                break
                
            # 既に同じ問題文が存在する場合はスキップ
            if question_data['text'] in existing_questions:
                continue
                
            question = Question.objects.create(
                level=level,
                question_type=question_type,
                question_text=question_data['text'],
                listening_text=question_data.get('listening_text', ''),
                image=question_data.get('image', '')
            )
            
            # 選択肢を作成
            for i, choice_text in enumerate(question_data['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(i == question_data['correct_index']),
                    order=i
                )
            
            created_count += 1
            existing_questions.add(question_data['text'])
            
        return created_count

    def _create_grammar_questions(self):
        """文法問題を作成"""
        questions = []
        # 基本的な文法パターンを定義
        patterns = [
            {'subject': ['I', 'You', 'He', 'She', 'We', 'They'],
             'verb': ['play', 'study', 'read', 'write', 'eat', 'drink', 'watch', 'listen to', 'speak', 'learn'],
             'object': ['soccer', 'tennis', 'baseball', 'basketball', 'English', 'Japanese', 'music', 'movies', 'books', 'games'],
             'time': ['every day', 'on weekends', 'after school', 'in the morning', 'in the evening', 'at night', 'on Monday', 'on Sunday', 'in summer', 'in winter']},
            {'subject': ['My friend', 'My sister', 'My brother', 'My mother', 'My father', 'The student', 'The teacher', 'The boy', 'The girl', 'The dog'],
             'verb': ['likes', 'loves', 'enjoys', 'wants', 'needs', 'has', 'makes', 'brings', 'takes', 'gives'],
             'object': ['apples', 'bananas', 'oranges', 'pizza', 'hamburgers', 'ice cream', 'chocolate', 'cookies', 'milk', 'juice'],
             'place': ['at home', 'at school', 'in the park', 'at the store', 'in the library', 'at the restaurant', 'in the garden', 'at the beach', 'in the classroom', 'at the station']}
        ]
        
        # 各パターンから問題を生成
        for pattern in patterns:
            for subject in pattern['subject']:
                for verb in pattern['verb']:
                    for obj in pattern['object']:
                        # 時間や場所の表現を選択
                        location = pattern.get('time', pattern.get('place', ['']))
                        for loc in location:
                            # 現在形の問題
                            question_text = f"{subject} (    ) {obj} {loc}."
                            base_verb = verb.split()[0]  # 複合動詞の場合は最初の部分だけ取る
                            
                            choices = [
                                base_verb + ('s' if subject in ['He', 'She', 'My friend', 'My sister', 'My brother', 'The student', 'The teacher', 'The boy', 'The girl', 'The dog'] else ''),
                                base_verb + ('s' if subject not in ['He', 'She', 'My friend', 'My sister', 'My brother', 'The student', 'The teacher', 'The boy', 'The girl', 'The dog'] else ''),
                                base_verb + 'ing',
                                base_verb + 'ed'
                            ]
                            
                            questions.append({
                                'text': question_text,
                                'choices': choices,
                                'correct_index': 0,
                                'explanation': f'主語が{subject}の場合、動詞は{choices[0]}を使います。'
                            })
                            
                            # 過去形の問題
                            question_text = f"{subject} (    ) {obj} {loc} yesterday."
                            choices = [
                                base_verb + 'ed',
                                base_verb,
                                base_verb + 's',
                                base_verb + 'ing'
                            ]
                            
                            questions.append({
                                'text': question_text,
                                'choices': choices,
                                'correct_index': 0,
                                'explanation': 'yesterdayがあるので過去形を使います。'
                            })
                            
                            if len(questions) >= 10:
                                return questions
        
        return questions

    def _create_conversation_questions(self):
        """会話問題を作成"""
        questions = []
        # 基本的な会話パターンを定義
        patterns = [
            {'question': ['How are you?', 'How do you feel?', 'How is it going?'],
             'answers': ['I\'m fine, thank you.', 'Not bad.', 'Pretty good.'],
             'wrong': ['Yes, I do.', 'No, I don\'t.', 'It\'s sunny.', 'At 3 o\'clock.']},
            {'question': ['What time is it?', 'Do you know the time?', 'Could you tell me the time?'],
             'answers': ['It\'s 3 o\'clock.', 'It\'s half past four.', 'It\'s quarter to six.'],
             'wrong': ['I\'m fine.', 'Yes, please.', 'It\'s sunny.', 'My name is Tom.']},
            {'question': ['What\'s the weather like today?', 'How\'s the weather?', 'What\'s it like outside?'],
             'answers': ['It\'s sunny.', 'It\'s raining.', 'It\'s cloudy.'],
             'wrong': ['I\'m fine.', 'At 3 o\'clock.', 'My name is Tom.', 'I\'m 12 years old.']},
            {'question': ['What\'s your name?', 'Could you tell me your name?', 'May I have your name?'],
             'answers': ['My name is Tom.', 'I\'m Mary.', 'I\'m John Smith.'],
             'wrong': ['I\'m fine.', 'It\'s sunny.', 'At 3 o\'clock.', 'I\'m 12 years old.']},
            {'question': ['How old are you?', 'What\'s your age?', 'Could you tell me your age?'],
             'answers': ['I\'m 12 years old.', 'I\'m 15.', 'I\'m thirteen.'],
             'wrong': ['My name is Tom.', 'It\'s sunny.', 'At 3 o\'clock.', 'I\'m fine.']},
            {'question': ['Where are you from?', 'What country are you from?', 'Where do you come from?'],
             'answers': ['I\'m from Japan.', 'I\'m from America.', 'I\'m from England.'],
             'wrong': ['I\'m fine.', 'It\'s sunny.', 'At 3 o\'clock.', 'My name is Tom.']},
            {'question': ['What do you like to do?', 'What are your hobbies?', 'What do you enjoy doing?'],
             'answers': ['I like to play soccer.', 'I enjoy reading books.', 'I like watching movies.'],
             'wrong': ['I\'m fine.', 'It\'s sunny.', 'At 3 o\'clock.', 'My name is Tom.']},
            {'question': ['Do you have any pets?', 'Do you have a pet?', 'What pets do you have?'],
             'answers': ['Yes, I have a dog.', 'Yes, I have a cat.', 'Yes, I have two dogs.'],
             'wrong': ['I\'m fine.', 'It\'s sunny.', 'At 3 o\'clock.', 'My name is Tom.']}
        ]
        
        # 各パターンから問題を生成
        for pattern in patterns:
            # 各パターンから1つの質問文と1つの回答をランダムに選択
            q = random.choice(pattern['question'])
            a = random.choice(pattern['answers'])
            wrong = random.sample(pattern['wrong'], 3)
            choices = [a] + wrong
            random.shuffle(choices)
            correct_index = choices.index(a)
            
            questions.append({
                'text': f'A: {q}\nB: (    )',
                'choices': choices,
                'correct_index': correct_index,
                'explanation': f'{q}に対する適切な返答は{a}です。'
            })
            
            if len(questions) >= 10:
                return questions
        
        return questions

    def _create_word_order_questions(self):
        """語句整序問題を作成"""
        questions = []
        # 基本的な文型パターンを定義
        patterns = [
            {'subject': ['I', 'you', 'he', 'she', 'we', 'they'],
             'verb': ['like', 'love', 'want', 'need', 'have'],
             'object': ['apples', 'bananas', 'books', 'games', 'music'],
             'format': '(1) {subject} (2) {verb} (3) {object}'},
            {'subject': ['I', 'you', 'he', 'she', 'we', 'they'],
             'verb': ['go', 'walk', 'run', 'study'],
             'place': ['to school', 'to the park', 'to the library', 'to the store'],
             'time': ['every day', 'on weekends', 'in the morning', 'after school'],
             'format': '(1) {subject} (2) {verb} (3) {place} (4) {time}'},
            {'subject': ['I', 'you', 'he', 'she', 'we', 'they'],
             'aux': ['can', 'will', 'must', 'should'],
             'verb': ['play', 'study', 'read', 'write'],
             'object': ['soccer', 'tennis', 'English', 'books'],
             'format': '(1) {subject} (2) {aux} (3) {verb} (4) {object}'}
        ]
        
        # 各パターンから問題を生成
        for pattern in patterns:
            for subj in pattern['subject']:
                for v in pattern['verb']:
                    for obj in pattern.get('object', ['']):
                        for place in pattern.get('place', ['']):
                            for time in pattern.get('time', ['']):
                                for aux in pattern.get('aux', ['']):
                                    # 文を組み立てる要素を準備
                                    elements = {
                                        'subject': subj,
                                        'verb': v,
                                        'object': obj,
                                        'place': place,
                                        'time': time,
                                        'aux': aux
                                    }
                                    
                                    # フォーマットに従って問題文を生成
                                    question_text = pattern['format'].format(**elements)
                                    
                                    # 正しい順序と3つの誤った順序を生成
                                    words = question_text.split('(')
                                    words = [w.strip(') ') for w in words if w.strip(') ')]
                                    correct_order = ''.join([str(i+1) for i in range(len(words)-1)])
                                    
                                    # 誤った順序を生成
                                    wrong_orders = []
                                    while len(wrong_orders) < 3:
                                        wrong = ''.join(random.sample(correct_order, len(correct_order)))
                                        if wrong != correct_order and wrong not in wrong_orders:
                                            wrong_orders.append(wrong)
                                    
                                    choices = [correct_order] + wrong_orders
                                    random.shuffle(choices)
                                    correct_index = choices.index(correct_order)
                                    
                                    questions.append({
                                        'text': f'次の語句を並び替えて正しい英文を作りなさい。\n\n{question_text}',
                                        'choices': choices,
                                        'correct_index': correct_index,
                                        'explanation': f'正しい語順は {correct_order} です。'
                                    })
                                    
                                    if len(questions) >= 10:
                                        return questions
        
        return questions

    def _create_reading_questions(self):
        """読解問題を作成"""
        questions = []
        # 基本的な読解文のパターンを定義
        passages = [
            {'text': '''Tom is a high school student who loves science. He spends most of his free time in the school laboratory, 
                    conducting experiments and learning about different scientific phenomena. His dream is to become a scientist 
                    and make important discoveries that will help people.''',
             'questions': [
                {'question': 'What does Tom want to be in the future?',
                 'choices': ['A scientist', 'A teacher', 'A doctor', 'An engineer']},
                {'question': 'Where does Tom spend most of his free time?',
                 'choices': ['In the school laboratory', 'In the library', 'In the classroom', 'In the gym']},
                {'question': 'What does Tom do in his free time?',
                 'choices': ['Conducts experiments', 'Plays sports', 'Reads books', 'Watches TV']}
             ]},
            {'text': '''Sarah has been studying French for three years. She practices speaking with her French teacher twice a week 
                    and watches French movies to improve her listening skills. Last summer, she visited Paris and was able to 
                    communicate with local people in French.''',
             'questions': [
                {'question': 'How long has Sarah been learning French?',
                 'choices': ['Three years', 'Two years', 'One year', 'Four years']},
                {'question': 'How often does she practice speaking French with her teacher?',
                 'choices': ['Twice a week', 'Once a week', 'Every day', 'Once a month']},
                {'question': 'Where did Sarah visit last summer?',
                 'choices': ['Paris', 'London', 'New York', 'Tokyo']}
             ]},
            {'text': '''The new shopping mall opened last month. It has more than 100 stores, including clothing shops, 
                    restaurants, and a movie theater. Many people visit the mall on weekends, and it has become a popular 
                    place for families to spend time together.''',
             'questions': [
                {'question': 'When did the shopping mall open?',
                 'choices': ['Last month', 'Last week', 'Last year', 'Two months ago']},
                {'question': 'How many stores does the mall have?',
                 'choices': ['More than 100', 'Less than 50', 'Exactly 100', 'About 50']},
                {'question': 'What is NOT mentioned as part of the mall?',
                 'choices': ['A library', 'Clothing shops', 'Restaurants', 'A movie theater']}
             ]}
        ]
        
        # 各パッセージから問題を生成
        for passage in passages:
            for q in passage['questions']:
                questions.append({
                    'text': passage['text'] + '\n\nQ: ' + q['question'],
                    'choices': q['choices'],
                    'correct_index': 0,
                    'explanation': f'本文から、{q["choices"][0]}が正解とわかります。'
                })
                
                if len(questions) >= 10:
                    return questions
        
        return questions

    def _create_listening_response_questions(self):
        """リスニング応答問題を作成"""
        questions = []
        # 基本的な応答パターンを定義
        patterns = [
            {'question': 'How are you?',
             'choices': ['I\'m fine, thank you.', 'It\'s three o\'clock.', 'My name is Tom.', 'I\'m from Japan.']},
            {'question': 'What time is it?',
             'choices': ['It\'s three o\'clock.', 'I\'m fine.', 'Nice to meet you.', 'Yes, please.']},
            {'question': 'What\'s your name?',
             'choices': ['My name is Tom.', 'I\'m fine.', 'It\'s sunny today.', 'Thank you very much.']},
            {'question': 'How\'s the weather today?',
             'choices': ['It\'s sunny.', 'I\'m twelve years old.', 'Nice to meet you.', 'You\'re welcome.']},
            {'question': 'Do you like English?',
             'choices': ['Yes, I do.', 'It\'s three o\'clock.', 'Thank you very much.', 'You\'re welcome.']}
        ]
        
        # 各パターンから問題を生成
        for pattern in patterns:
            questions.append({
                'text': '音声を聞いて、適切な応答を選びなさい。',
                'listening_text': pattern['question'],
                'choices': pattern['choices'],
                'correct_index': 0,
                'explanation': f'{pattern["question"]}に対する適切な返答は{pattern["choices"][0]}です。'
            })
            
            if len(questions) >= 10:
                return questions
        
        return questions

    def _create_listening_conversation_questions(self):
        """リスニング会話問題を作成"""
        questions = []
        # 基本的な会話パターンを定義
        conversations = [
            {'text': '''A: What time do you go to school?
                    B: I go to school at 8:30.
                    A: Do you walk to school?
                    B: No, I take the bus.''',
             'choices': [
                'The student goes to school at 8:30 by bus.',
                'The student goes to school at 9:00 by bus.',
                'The student goes to school at 8:30 on foot.',
                'The student goes to school at 9:00 on foot.'
             ]},
            {'text': '''A: What do you like to do in your free time?
                    B: I like to play soccer and read books.
                    A: How often do you play soccer?
                    B: I play soccer every weekend.''',
             'choices': [
                'The person plays soccer every weekend and likes reading books.',
                'The person plays soccer every day and likes reading books.',
                'The person plays soccer every weekend and likes watching TV.',
                'The person plays soccer every day and likes watching TV.'
             ]},
            {'text': '''A: How many people are in your family?
                    B: There are four people in my family.
                    A: Who are they?
                    B: My father, mother, sister, and me.''',
             'choices': [
                'There are four people in the family: father, mother, sister, and the speaker.',
                'There are three people in the family: father, mother, and the speaker.',
                'There are four people in the family: father, mother, brother, and the speaker.',
                'There are three people in the family: father, mother, and sister.'
             ]}
        ]
        
        # 各会話から問題を生成
        for conv in conversations:
            questions.append({
                'text': '音声を聞いて、会話の内容に一致するものを選びなさい。',
                'listening_text': conv['text'],
                'choices': conv['choices'],
                'correct_index': 0,
                'explanation': '会話の内容から、' + conv['choices'][0] + 'が正解です。'
            })
            
            if len(questions) >= 10:
                return questions
        
        return questions

    def _create_listening_short_passage_questions(self):
        """リスニング短文問題を作成"""
        questions = []
        # 基本的な短文パターンを定義
        passages = [
            {'text': '''Tom is a student. He goes to school by bus every day. 
                    His school starts at 8:30. He likes math and science.''',
             'choices': [
                'Tom goes to school by bus and likes math and science.',
                'Tom goes to school on foot and likes math and science.',
                'Tom goes to school by bus and likes English and history.',
                'Tom goes to school on foot and likes English and history.'
             ]},
            {'text': '''Mary has a cat. Its name is Tama. Tama is 3 years old. 
                    It likes to play with a ball.''',
             'choices': [
                'Mary\'s cat is 3 years old and likes to play with a ball.',
                'Mary\'s cat is 5 years old and likes to play with a ball.',
                'Mary\'s cat is 3 years old and likes to sleep.',
                'Mary\'s cat is 5 years old and likes to sleep.'
             ]},
            {'text': '''John likes to play soccer. He plays with his friends every weekend. 
                    He also likes to read books about animals.''',
             'choices': [
                'John plays soccer every weekend and likes reading books about animals.',
                'John plays soccer every day and likes reading books about animals.',
                'John plays soccer every weekend and likes watching TV.',
                'John plays soccer every day and likes watching TV.'
             ]}
        ]
        
        # 各短文から問題を生成
        for passage in passages:
            questions.append({
                'text': '音声を聞いて、内容に一致するものを選びなさい。',
                'listening_text': passage['text'],
                'choices': passage['choices'],
                'correct_index': 0,
                'explanation': '音声の内容から、' + passage['choices'][0] + 'が正解です。'
            })
            
            if len(questions) >= 10:
                return questions
        
        return questions

    def _create_listening_illustration_questions(self):
        """リスニングイラスト問題を作成"""
        questions = []
        return questions 