from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Choice, UserAnswer, UserProgress, ReadingUserAnswer
from django.db.models import Count, Q
import random
from django.http import JsonResponse
from django.contrib import messages
import json
from questions.models import ReadingPassage, ReadingQuestion, ReadingChoice, ListeningQuestion, ListeningUserAnswer, ListeningChoice
from django.urls import reverse
from django.utils import timezone

@login_required
def exam_list(request):
    """試験一覧を表示"""
    # 級の定義（Grade 4のみ）
    levels = [
        ('4', 'Grade 4'),
    ]
    
    # 問題タイプの定義
    question_types = {
        'grammar_fill': '文法・語彙問題',
        'conversation_fill': '会話補充問題',
        'word_order': '語順選択問題',
        'reading_comprehension': '長文読解問題',
        'listening_conversation': 'リスニング第2部: 会話問題',
        'listening_illustration': 'リスニング第1部: イラスト問題',
        'listening_passage': 'リスニング第3部: 文章問題',
        'random': 'ランダム10問',
        'mock_exam': '模擬試験問題',
    }
    
    # Grade 4の問題数を取得
    question_counts = {}
    for q_type in question_types.keys():
        if q_type == 'listening_illustration':
            count = ListeningQuestion.objects.filter(level='4').count()
        elif q_type == 'reading_comprehension':
            count = ReadingPassage.objects.filter(level='4').count()
        else:
            count = Question.objects.filter(level='4', question_type=q_type).count()
        question_counts[q_type] = count
    
        context = {
        'levels': levels,
        'question_types': question_types,
        'question_counts': question_counts,
    }
    
    return render(request, 'exams/exam_list.html', context)

@login_required
def question_list(request, level=None, exam_id=None):
    question_type = request.GET.get('type')
    
    # デバッグ出力を追加
    print(f"Debug - question_list called with level={level}, exam_id={exam_id}, question_type={question_type}")
    print(f"Debug - request.GET: {request.GET}")
    print(f"Debug - request.path: {request.path}")
    
    # 長文読解以外はデフォルト5問、長文読解はデフォルト3問
    if question_type == 'reading_comprehension':
        num_questions_param = request.GET.get('num_questions', 3)
        if num_questions_param == 'all':
            num_questions = 'all'
        else:
            num_questions = int(num_questions_param)
    else:
        num_questions_param = request.GET.get('num_questions', 5)
        if num_questions_param == 'all':
            num_questions = 'all'
        else:
            num_questions = int(num_questions_param)
    
    status = request.GET.get('status', 'all')
    
    print(f"Debug - Level: {level}, Question Type: {question_type}")  # デバッグ出力
    
    # 問題タイプの定義
    question_types = {
        'grammar_fill': '文法・語彙問題',
        'conversation_fill': '会話補充問題',
        'word_order': '語順選択問題',
        'reading_comprehension': '長文読解問題',
        'listening_conversation': 'リスニング第2部: 会話問題',
        'listening_illustration': 'リスニング第1部: イラスト問題',
        'listening_passage': 'リスニング第3部: 文章問題',
        'random': 'ランダム10問',
        'mock_exam': '模擬試験問題',
    }
    
    # 問題数のオプション（長文読解以外）
    question_count_options = {
        3: '3問',
        5: '5問',
        10: '10問',
        20: '20問',
        30: '30問',
        'all': '全て',
    }
    
    # 長文読解問題専用のオプション（1問を含む）
    if question_type == 'reading_comprehension':
        question_count_options = {
            1: '1本文',
            3: '3本文',
            5: '5本文',
            10: '10本文',
            20: '20本文',
            30: '30本文',
            'all': '全て',
        }
    
    if question_type == 'random':
        # ランダム10問の場合
        all_questions = []
        
        # カテゴリーの日本語名マッピング
        category_names = {
            'grammar_fill': '文法・語彙問題',
            'conversation_fill': '会話補充問題',
            'word_order': '語順選択問題',
            'listening_conversation': 'リスニング会話問題',
            'listening_passage': 'リスニング文章問題',
            'listening_illustration': 'リスニングイラスト問題',
        }
        
        # 各カテゴリーから問題を取得
        categories = [
            ('grammar_fill', Question),
            ('conversation_fill', Question),
            ('word_order', Question),
            ('listening_conversation', Question),
            ('listening_passage', Question),
            ('listening_illustration', ListeningQuestion),
        ]
        
        # 各カテゴリーから2問ずつ取得（合計12問、その後10問に絞る）
        for category_type, model_class in categories:
            if model_class == ListeningQuestion:
                questions = model_class.objects.filter(level=level).order_by('?')[:2]
            else:
                questions = model_class.objects.filter(level=level, question_type=category_type).order_by('?')[:2]
            
            for question in questions:
                if model_class == ListeningQuestion:
                    choices = ListeningChoice.objects.filter(question=question).order_by('order')
                    all_questions.append({
                        'question': question,
                        'choices': choices,
                        'user_answer': None,
                        'is_correct': None,
                        'explanation': getattr(question, 'explanation', ''),
                        'category': category_type,
                        'category_name': category_names.get(category_type, category_type),
                        'question_type': 'listening_illustration'
                    })
                else:
                    choices = Choice.objects.filter(question=question).order_by('order')
                    correct_choice = choices.filter(is_correct=True).first()
                    all_questions.append({
                        'question': question,
                        'choices': choices,
                        'user_answer': None,
                        'correct_choice': correct_choice,
                        'explanation': question.explanation,
                        'category': category_type,
                        'category_name': category_names.get(category_type, category_type),
                        'question_type': category_type
                    })
        
        # 10問に絞る
        if len(all_questions) > 10:
            all_questions = random.sample(all_questions, 10)
        
        context = {
            'level': level,
            'question_type': question_type,
            'question_type_display': question_types.get(question_type, ''),
            'num_questions': 10,
            'status': status,
            'questions': all_questions,
            'question_count_options': question_count_options,
        }
        return render(request, 'exams/question_list.html', context)
    
    elif question_type == 'mock_exam':
        # 模擬試験問題の場合（英検4級の実際の問題構成）
        all_questions = []
        reading_passages = []
        
        # カテゴリーの日本語名マッピング（統一された名前）
        category_names = {
            'grammar_fill': '文法・語彙問題',
            'conversation_fill': '会話補充問題',
            'word_order': '語順選択問題',
            'reading_comprehension': '長文読解問題',
            'listening_illustration': 'リスニングイラスト問題',
            'listening_conversation': 'リスニング会話問題',
            'listening_passage': 'リスニング文章問題',
        }
        
        # 英検4級の実際の問題構成（順序付き）
        exam_structure = [
            ('grammar_fill', Question, 15),      # 大問1: 15問
            ('conversation_fill', Question, 5),  # 大問2: 5問
            ('word_order', Question, 5),         # 大問3: 5問
            ('reading_comprehension', ReadingPassage, 3),  # 大問4: 3パッセージ（約10問）
            ('listening_illustration', ListeningQuestion, 10),  # 第1部: 10問
            ('listening_conversation', Question, 10),      # 第2部: 10問
            ('listening_passage', Question, 10),           # 第3部: 10問
        ]
        
        # 各カテゴリーから指定された数の問題を取得
        question_counter = 1
        regular_questions = []  # 通常の問題（大問1-3）
        reading_passages = []   # 長文読解問題（大問4）
        listening_questions = [] # リスニング問題（第1-3部）
        
        for category_type, model_class, num_questions in exam_structure:
            if model_class == ListeningQuestion:
                questions = model_class.objects.filter(level=level).order_by('?')[:num_questions]
                for question in questions:
                    choices = ListeningChoice.objects.filter(question=question).order_by('order')
                    listening_questions.append({
                        'question': question,
                        'choices': choices,
                        'user_answer': None,
                        'is_correct': None,
                        'explanation': getattr(question, 'explanation', ''),
                        'category': category_type,
                        'category_name': category_names.get(category_type, category_type),
                        'question_type': 'listening_illustration',
                        'category_order': exam_structure.index((category_type, model_class, num_questions)),
                        'question_number': question_counter
                    })
                    question_counter += 1
            elif model_class == ReadingPassage:
                passages = model_class.objects.filter(level=level).order_by('?')[:num_questions]
                # パッセージから問題を取得
                for passage in passages:
                    passage_questions = ReadingQuestion.objects.filter(passage=passage).order_by('question_number')
                    questions_with_answers = []
                    for question in passage_questions:
                        choices = ReadingChoice.objects.filter(question=question).order_by('order')
                        correct_choice = choices.filter(is_correct=True).first()
                        questions_with_answers.append({
                            'question': question,
                            'choices': choices,
                            'user_answer': None,
                            'correct_choice': correct_choice,
                            'explanation': getattr(question, 'explanation', ''),
                            'question_number': question_counter
                        })
                        question_counter += 1
                    reading_passages.append({
                        'passage': passage,
                        'questions': questions_with_answers,
                        'category_order': exam_structure.index((category_type, model_class, num_questions))
                    })
            else:
                questions = model_class.objects.filter(level=level, question_type=category_type).order_by('?')[:num_questions]
                for question in questions:
                    choices = Choice.objects.filter(question=question).order_by('order')
                    correct_choice = choices.filter(is_correct=True).first()
                    
                    # リスニング問題かどうかを判定
                    if category_type in ['listening_conversation', 'listening_passage']:
                        listening_questions.append({
                            'question': question,
                            'choices': choices,
                            'user_answer': None,
                            'correct_choice': correct_choice,
                            'explanation': question.explanation,
                            'category': category_type,
                            'category_name': category_names.get(category_type, category_type),
                            'question_type': category_type,
                            'category_order': exam_structure.index((category_type, model_class, num_questions)),
                            'question_number': question_counter
                        })
                    else:
                        regular_questions.append({
                            'question': question,
                            'choices': choices,
                            'user_answer': None,
                            'correct_choice': correct_choice,
                            'explanation': question.explanation,
                            'category': category_type,
                            'category_name': category_names.get(category_type, category_type),
                            'question_type': category_type,
                            'category_order': exam_structure.index((category_type, model_class, num_questions)),
                            'question_number': question_counter
                        })
                    question_counter += 1
        
        # カテゴリー順序でソート
        regular_questions.sort(key=lambda x: x['category_order'])
        listening_questions.sort(key=lambda x: x['category_order'])
        
        # 英検4級の実際の順序で結合（リスニング問題は順序通り）
        all_questions = regular_questions + listening_questions
        
        # 長文読解問題がある場合は専用テンプレートを使用
        if reading_passages:
            # リスニング問題を正しい順序で分離
            listening_illustration = [q for q in listening_questions if q['category'] == 'listening_illustration']
            listening_conversation = [q for q in listening_questions if q['category'] == 'listening_conversation']
            listening_passage = [q for q in listening_questions if q['category'] == 'listening_passage']
            
            context = {
                'level': level,
                'question_type': question_type,
                'question_type_display': question_types.get(question_type, ''),
                'num_questions': len(all_questions) + sum(len(p['questions']) for p in reading_passages),
                'status': status,
                'questions': all_questions,
                'passages': reading_passages,
                'listening_illustration': listening_illustration,
                'listening_conversation': listening_conversation,
                'listening_passage': listening_passage,
                'question_count_options': question_count_options,
            }
            return render(request, 'exams/mock_exam.html', context)
        else:
            context = {
                'level': level,
                'question_type': question_type,
                'question_type_display': question_types.get(question_type, ''),
                'num_questions': len(all_questions),
                'status': status,
                'questions': all_questions,
                'question_count_options': question_count_options,
            }
            return render(request, 'exams/question_list.html', context)
    
    elif question_type == 'listening_illustration':
        # イラスト問題の場合
        questions = ListeningQuestion.objects.filter(level=level).order_by('id')
        print(f"Debug - Listening Illustration Questions: {questions.count()}")  # デバッグ出力
        
        # 「全て」が選択された場合は制限しない
        if num_questions != 'all' and len(questions) > num_questions:
            questions = random.sample(list(questions), num_questions)
            questions.sort(key=lambda x: x.id)
        
        # 問題と選択肢を組み合わせる（回答履歴は表示しない）
        questions_with_choices = []
        for question in questions:
            choices = ListeningChoice.objects.filter(question=question).order_by('order')
            questions_with_choices.append({
                'question': question,
                'choices': choices,
                'user_answer': None,  # 常にNoneにして未選択状態にする
                'is_correct': None,
                'explanation': getattr(question, 'explanation', '')
            })
        
        context = {
            'level': level,
            'question_type': question_type,
            'question_type_display': question_types.get(question_type, ''),
            'num_questions': num_questions,
            'status': status,
            'questions': questions_with_choices,
            'question_count_options': question_count_options,
        }
        return render(request, 'exams/question_list.html', context)
    
    elif question_type in ['listening_conversation', 'listening_passage']:
        # リスニング会話問題とリスニング文章問題の場合
        questions = Question.objects.filter(level=level, question_type=question_type).order_by('question_number')
        print(f"Debug - Regular Questions: {questions.count()}")  # デバッグ出力
        questions = list(questions)
        
        # ユーザーの回答履歴を取得
        user_answers = UserAnswer.objects.filter(
            user=request.user,
            question__in=questions
        ).select_related('question', 'selected_choice')
        
        # 問題IDをキーとした回答辞書を作成
        user_answer_dict = {answer.question.id: answer for answer in user_answers}
        
        # 状態フィルターに応じて問題をフィルタリング
        if status == 'unanswered':
            # 未回答の問題のみ
            questions = [q for q in questions if q.id not in user_answer_dict]
        elif status == 'correct':
            # 正解の問題のみ
            questions = [q for q in questions if q.id in user_answer_dict and user_answer_dict[q.id].is_correct]
        elif status == 'incorrect':
            # 不正解の問題のみ
            questions = [q for q in questions if q.id in user_answer_dict and not user_answer_dict[q.id].is_correct]
        # status == 'all' の場合は全ての問題を表示
        
        # デバッグ出力を追加
        print(f"Debug - user_answer_dict keys: {list(user_answer_dict.keys())}")
        print(f"Debug - questions after filter: {[q.id for q in questions]}")
        print(f"Debug - status: {status}")
        
        # 問題数制限を適用
        if num_questions != 'all' and len(questions) > num_questions:
            questions = random.sample(questions, num_questions)
            questions.sort(key=lambda x: x.question_number)
        
        # POSTリクエストがある場合のみ回答処理を実行
        if request.method == 'POST':
            # POSTされたquestion_idをすべて取得
            post_question_ids = [
                int(key.replace('answer_', ''))
                for key in request.POST.keys()
                if key.startswith('answer_')
            ]
            
            # 既存の回答を削除（POSTされたquestion_idのみ）
            UserAnswer.objects.filter(
                user=request.user,
                question_id__in=post_question_ids
            ).delete()
            
            # 回答を保存
            for question_id in post_question_ids:
                answer_key = f'answer_{question_id}'
                selected_choice_id = request.POST.get(answer_key)
                if selected_choice_id:
                    choice = Choice.objects.get(id=selected_choice_id)
                    is_correct = choice.is_correct
                    question = Question.objects.get(id=question_id)
                    UserAnswer.objects.create(
                        user=request.user,
                        question=question,
                        selected_choice=choice,
                        is_correct=is_correct
                    )
                    # 進捗を更新
                    update_user_progress(request.user, level, question_type, is_correct)

            # 今回回答したquestion_idと出題順序をセッションに保存
            request.session[f'answered_questions_{question_type}_{level}'] = post_question_ids

            return redirect('exams:answer_results', level=level, question_type=question_type)
        
        # GETリクエストの場合は問題を表示
        # 問題と回答を組み合わせる
        questions_with_answers = []
        for question in questions:
            choices = Choice.objects.filter(question=question).order_by('order')
            correct_choice = choices.filter(is_correct=True).first()
            user_answer = user_answer_dict.get(question.id)
            
            questions_with_answers.append({
                'question': question,
                'choices': choices,
                'user_answer': user_answer.selected_choice if user_answer else None,
                'is_correct': user_answer.is_correct if user_answer else None,
                'correct_choice': correct_choice,
                'explanation': question.explanation
            })
        
        context = {
            'level': level,
            'question_type': question_type,
            'question_type_display': question_types.get(question_type, ''),
            'num_questions': num_questions,
            'status': status,
            'questions': questions_with_answers,
            'question_count_options': question_count_options,
        }
        return render(request, 'exams/question_list.html', context)

    elif question_type == 'reading_comprehension':
        # 長文読解問題の場合
        passages = list(ReadingPassage.objects.filter(level=level).order_by('id'))
        print(f"Debug - Reading Passages: {len(passages)}")  # デバッグ出力
        
        # 「全て」が選択された場合は制限しない
        if num_questions != 'all' and len(passages) > num_questions:
            passages = random.sample(passages, num_questions)
            passages.sort(key=lambda x: x.id)
        
        # 出題時のパッセージ順序をセッションに保存
        passage_order = {passage.id: index for index, passage in enumerate(passages)}
        request.session[f'passage_order_{question_type}_{level}'] = passage_order
        
        # パッセージと問題を組み合わせる
        passages_with_questions = []
        for passage in passages:
            passage_questions = ReadingQuestion.objects.filter(passage=passage).order_by('question_number')
            
            # ユーザーの回答を取得
            user_answers = {}
            answers = ReadingUserAnswer.objects.filter(
                user=request.user,
                reading_question__in=passage_questions
            )
            for answer in answers:
                user_answers[answer.reading_question.id] = answer.selected_reading_choice
            
            # 問題と回答を組み合わせる
            questions_with_answers = []
            for question in passage_questions:
                choices = ReadingChoice.objects.filter(question=question).order_by('order')
                correct_choice = choices.filter(is_correct=True).first()
                questions_with_answers.append({
                    'question': question,
                    'choices': choices,
                    'user_answer': user_answers.get(question.id),
                    'correct_choice': correct_choice,
                    'explanation': getattr(question, 'explanation', '')
                })
            
            passages_with_questions.append({
                'passage': passage,
                'questions': questions_with_answers
            })
        
        context = {
            'level': level,
            'question_type': question_type,
            'question_type_display': question_types.get(question_type, ''),
            'num_questions': num_questions,
            'status': status,
            'passages': passages_with_questions,
            'question_count_options': question_count_options,
        }
        return render(request, 'exams/reading_comprehension.html', context)
    
    else:
        # 通常の問題の場合
        questions = Question.objects.filter(level=level, question_type=question_type).order_by('question_number')
        print(f"Debug - Regular Questions: {questions.count()}")  # デバッグ出力
        questions = list(questions)
        
        # ユーザーの回答履歴を取得
        user_answers = UserAnswer.objects.filter(
            user=request.user,
            question__in=questions
        ).select_related('question', 'selected_choice')
        
        # 問題IDをキーとした回答辞書を作成
        user_answer_dict = {answer.question.id: answer for answer in user_answers}
        
        # 状態フィルターに応じて問題をフィルタリング
        if status == 'unanswered':
            # 未回答の問題のみ
            questions = [q for q in questions if q.id not in user_answer_dict]
        elif status == 'correct':
            # 正解の問題のみ
            questions = [q for q in questions if q.id in user_answer_dict and user_answer_dict[q.id].is_correct]
        elif status == 'incorrect':
            # 不正解の問題のみ
            questions = [q for q in questions if q.id in user_answer_dict and not user_answer_dict[q.id].is_correct]
        # status == 'all' の場合は全ての問題を表示
        
        # デバッグ出力を追加
        print(f"Debug - user_answer_dict keys: {list(user_answer_dict.keys())}")
        print(f"Debug - questions after filter: {[q.id for q in questions]}")
        print(f"Debug - status: {status}")
        
        # 問題数制限を適用
        if num_questions != 'all' and len(questions) > num_questions:
            questions = random.sample(questions, num_questions)
            questions.sort(key=lambda x: x.question_number)
        
        # POSTリクエストがある場合のみ回答処理を実行
        if request.method == 'POST':
            # POSTされたquestion_idをすべて取得
            post_question_ids = [
                int(key.replace('answer_', ''))
                for key in request.POST.keys()
                if key.startswith('answer_')
            ]
            
            # 既存の回答を削除（POSTされたquestion_idのみ）
            UserAnswer.objects.filter(
                user=request.user,
                question_id__in=post_question_ids
            ).delete()
            
            # 回答を保存
            for question_id in post_question_ids:
                answer_key = f'answer_{question_id}'
                selected_choice_id = request.POST.get(answer_key)
                if selected_choice_id:
                    choice = Choice.objects.get(id=selected_choice_id)
                    is_correct = choice.is_correct
                    question = Question.objects.get(id=question_id)
                    UserAnswer.objects.create(
                        user=request.user,
                        question=question,
                        selected_choice=choice,
                        is_correct=is_correct
                    )
                    # 進捗を更新
                    update_user_progress(request.user, level, question_type, is_correct)

            # 今回回答したquestion_idと出題順序をセッションに保存
            request.session[f'answered_questions_{question_type}_{level}'] = post_question_ids

            return redirect('exams:answer_results', level=level, question_type=question_type)
        
        # GETリクエストの場合は問題を表示
        # 問題と回答を組み合わせる
        questions_with_answers = []
        for question in questions:
            choices = Choice.objects.filter(question=question).order_by('order')
            correct_choice = choices.filter(is_correct=True).first()
            user_answer = user_answer_dict.get(question.id)
            
            questions_with_answers.append({
                'question': question,
                'choices': choices,
                'user_answer': user_answer.selected_choice if user_answer else None,
                'is_correct': user_answer.is_correct if user_answer else None,
                'correct_choice': correct_choice,
                'explanation': question.explanation
            })
        
        context = {
            'level': level,
            'question_type': question_type,
            'question_type_display': question_types.get(question_type, ''),
            'num_questions': num_questions,
            'status': status,
            'questions': questions_with_answers,
            'question_count_options': question_count_options,
        }
        return render(request, 'exams/question_list.html', context)

@login_required
def question_detail(request, question_id):
    """問題の詳細を表示"""
    question = get_object_or_404(Question, id=question_id)
    choices = question.choices.all().order_by('order')
    
    # 再挑戦パラメータが指定されている場合は回答履歴を削除
    if request.GET.get('retry'):
        UserAnswer.objects.filter(user=request.user, question=question).delete()
        return redirect('exams:question_detail', question_id=question_id)
    
    # ユーザーの最新の回答を取得
    user_answer = UserAnswer.objects.filter(
        user=request.user,
        question=question
    ).order_by('-answered_at').first()
    
    return render(request, 'exams/question_detail.html', {
        'question': question,
        'choices': choices,
        'user_answer': user_answer
    })

@login_required
def submit_answer(request, question_id):
    """回答を提出"""
    question = get_object_or_404(Question, id=question_id)
    choice_id = request.POST.get('choice')
    
    if choice_id:
        choice = get_object_or_404(Choice, id=choice_id)
        UserAnswer.objects.create(
            user=request.user,
            question=question,
            selected_choice=choice,
            is_correct=choice.is_correct
        )
        # 進捗を更新
        update_user_progress(request.user, question.level, question.question_type, choice.is_correct)
        messages.success(request, '回答を保存しました。')
    
    return redirect('exams:question_list', level=question.level)

@login_required
def submit_reading_comprehension(request, level):
    """長文読解問題の回答を提出"""
    if request.method == 'POST':
        # 既存の回答を削除
        ReadingUserAnswer.objects.filter(
            user=request.user,
            reading_question__passage__level=level
        ).delete()
        
        # POSTデータから回答を取得し、順序を保持
        answers = []
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                answers.append((int(question_id), value))
        
        # 問題IDでソートして順序を保持
        answers.sort(key=lambda x: x[0])
        
        # 回答を保存（順序を保持）
        for question_id, choice_id in answers:
            try:
                question = ReadingQuestion.objects.get(id=question_id)
                choice = ReadingChoice.objects.get(id=choice_id)
                
                # 回答を保存
                ReadingUserAnswer.objects.create(
                    user=request.user,
                    reading_question=question,
                    selected_reading_choice=choice,
                    is_correct=choice.is_correct
                )
                
                # 進捗を更新
                update_user_progress(request.user, level, 'reading_comprehension', choice.is_correct)
                
            except (ReadingQuestion.DoesNotExist, ReadingChoice.DoesNotExist):
                messages.error(request, f'問題 {question_id} の選択肢が見つかりませんでした。')
                continue
        
        messages.success(request, '回答を保存しました。')
        return redirect('exams:answer_results', level=level, question_type='reading_comprehension')
    
    return redirect('exams:question_list', level=level, type='reading_comprehension')

@login_required
def submit_answers(request, level):
    if request.method == 'POST':
        question_type = request.POST.get('question_type')
        level = int(level)  # URLパラメータから取得したlevelを使用
        status = request.POST.get('status', 'all')  # 追加
        # num_questionsが「全て」の場合は文字列、そうでなければ整数
        num_questions_param = request.POST.get('num_questions', 10)
        if num_questions_param == 'all':
            num_questions = 'all'
        else:
            num_questions = int(num_questions_param)
        
        print(f"Debug - Submit Answers: question_type={question_type}, level={level}, num_questions={num_questions}")
        print(f"Debug - POST data: {request.POST}")
        
        if question_type == 'random':
            # ランダム10問の場合
            # POSTされたquestion_idをすべて取得
            post_question_ids = [
                int(key.replace('answer_', ''))
                for key in request.POST.keys()
                if key.startswith('answer_')
            ]
            
            # 各問題のタイプを判定して適切な回答を保存
            for question_id in post_question_ids:
                answer_key = f'answer_{question_id}'
                if answer_key in request.POST:
                    selected_answer = request.POST.get(answer_key)
                    
                    # リスニングイラスト問題かどうかを判定
                    try:
                        question = ListeningQuestion.objects.get(id=question_id)
                        # リスニングイラスト問題の場合
                        is_correct = selected_answer == question.correct_answer
                        ListeningUserAnswer.objects.create(
                            user=request.user,
                            question=question,
                            selected_answer=selected_answer,
                            is_correct=is_correct
                        )
                        # 進捗を更新
                        update_user_progress(request.user, level, 'listening_illustration', is_correct)
                    except ListeningQuestion.DoesNotExist:
                        # 通常の問題の場合
                        try:
                            question = Question.objects.get(id=question_id)
                            choice = Choice.objects.get(id=selected_answer)
                            UserAnswer.objects.create(
                                user=request.user,
                                question=question,
                                selected_choice=choice,
                                is_correct=choice.is_correct
                            )
                            # 進捗を更新
                            update_user_progress(request.user, level, question.question_type, choice.is_correct)
                        except (Question.DoesNotExist, Choice.DoesNotExist):
                            continue
            
            # 今回回答したquestion_idをセッションに保存
            request.session[f'answered_questions_{question_type}_{level}'] = post_question_ids
            
            return redirect('exams:answer_results', level=level, question_type=question_type)
        
        elif question_type == 'listening_illustration':
            # イラスト問題の場合
            questions = ListeningQuestion.objects.filter(level=level).order_by('id')
            # 「全て」が選択された場合は制限しない
            if num_questions != 'all' and len(questions) > num_questions:
                questions = random.sample(list(questions), num_questions)
                questions.sort(key=lambda x: x.id)
            
            # POSTされたquestion_idをすべて取得
            post_question_ids = [
                int(key.replace('answer_', ''))
                for key in request.POST.keys()
                if key.startswith('answer_')
            ]
            
            # 既存の回答を削除（POSTされたquestion_idのみ）
            ListeningUserAnswer.objects.filter(
                user=request.user,
                question_id__in=post_question_ids
            ).delete()
                
            # 回答を保存
            for question_id in post_question_ids:
                answer_key = f'answer_{question_id}'
                if answer_key in request.POST:
                    selected_answer = request.POST.get(answer_key)
                    question = ListeningQuestion.objects.get(id=question_id)
                    is_correct = selected_answer == question.correct_answer
                    ListeningUserAnswer.objects.create(
                        user=request.user,
                        question=question,
                        selected_answer=selected_answer,
                        is_correct=is_correct
                    )
                    # 進捗を更新
                    update_user_progress(request.user, level, 'listening_illustration', is_correct)
            
            # 今回回答したquestion_idと出題順序をセッションに保存
            request.session[f'answered_questions_{question_type}_{level}'] = post_question_ids
            
            return redirect('exams:answer_results', level=level, question_type=question_type)
        
        elif question_type in ['listening_conversation', 'listening_passage']:
            # その他のリスニング問題の場合
            questions = Question.objects.filter(level=level, question_type=question_type).order_by('question_number')
            questions = list(questions)
            # 「全て」が選択された場合は制限しない
            if num_questions != 'all' and len(questions) > num_questions:
                questions = random.sample(questions, num_questions)
                questions.sort(key=lambda x: x.question_number)
            
            # POSTされたquestion_idをすべて取得
            post_question_ids = [
                int(key.replace('answer_', ''))
                for key in request.POST.keys()
                if key.startswith('answer_')
            ]

            # 既存の回答を削除（POSTされたquestion_idのみ）
            UserAnswer.objects.filter(
                user=request.user,
                question_id__in=post_question_ids
            ).delete()
            
            # 回答を保存
            for question_id in post_question_ids:
                answer_key = f'answer_{question_id}'
                selected_choice_id = request.POST.get(answer_key)
                if selected_choice_id:
                    choice = Choice.objects.get(id=selected_choice_id)
                    is_correct = choice.is_correct
                    question = Question.objects.get(id=question_id)
                    UserAnswer.objects.create(
                        user=request.user,
                        question=question,
                        selected_choice=choice,
                        is_correct=is_correct
                    )
                    # 進捗を更新
                    update_user_progress(request.user, level, question_type, is_correct)
            
            # 今回回答したquestion_idと出題順序をセッションに保存
            request.session[f'answered_questions_{question_type}_{level}'] = post_question_ids
            
            return redirect('exams:answer_results', level=level, question_type=question_type)
        
        elif question_type == 'reading_comprehension':
            # 長文読解問題の場合
            passages = ReadingPassage.objects.filter(level=level).order_by('id')
            # 「全て」が選択された場合は制限しない
            if num_questions != 'all' and len(passages) > num_questions:
                passages = random.sample(list(passages), num_questions)
                passages.sort(key=lambda x: x.id)
            
            # POSTされたquestion_idをすべて取得
            post_question_ids = [
                int(key.replace('answer_', ''))
                for key in request.POST.keys()
                if key.startswith('answer_')
            ]

            # 既存の回答を削除（POSTされたquestion_idのみ）
            ReadingUserAnswer.objects.filter(
                user=request.user,
                reading_question_id__in=post_question_ids
            ).delete()

            # 回答を保存
            for question_id in post_question_ids:
                answer_key = f'answer_{question_id}'
                selected_choice_id = request.POST.get(answer_key)
                if selected_choice_id:
                    choice = ReadingChoice.objects.get(id=selected_choice_id)
                    is_correct = choice.is_correct
                    question = ReadingQuestion.objects.get(id=question_id)
                    ReadingUserAnswer.objects.create(
                        user=request.user,
                        reading_question=question,
                        selected_reading_choice=choice,
                        is_correct=is_correct
                    )
                # 進捗を更新
                    update_user_progress(request.user, level, 'reading_comprehension', is_correct)

            # 今回回答したquestion_idと出題順序をセッションに保存
            request.session[f'answered_questions_{question_type}_{level}'] = post_question_ids
            
            return redirect('exams:answer_results', level=level, question_type=question_type)
        
        else:
            # 通常の問題の場合
            questions = Question.objects.filter(level=level, question_type=question_type).order_by('question_number')
            print(f"Debug - Regular Questions: {questions.count()}")  # デバッグ出力
            questions = list(questions)
            
            # ユーザーの回答履歴を取得
            user_answers = UserAnswer.objects.filter(
                    user=request.user,
                question__in=questions
            ).select_related('question', 'selected_choice')
            
            # 問題IDをキーとした回答辞書を作成
            user_answer_dict = {answer.question.id: answer for answer in user_answers}
            
            # 状態フィルターに応じて問題をフィルタリング
            if status == 'unanswered':
                # 未回答の問題のみ
                questions = [q for q in questions if q.id not in user_answer_dict]
            elif status == 'correct':
                # 正解の問題のみ
                questions = [q for q in questions if q.id in user_answer_dict and user_answer_dict[q.id].is_correct]
            elif status == 'incorrect':
                # 不正解の問題のみ
                questions = [q for q in questions if q.id in user_answer_dict and not user_answer_dict[q.id].is_correct]
            # status == 'all' の場合は全ての問題を表示
            
            # デバッグ出力を追加
            print(f"Debug - user_answer_dict keys: {list(user_answer_dict.keys())}")
            print(f"Debug - questions after filter: {[q.id for q in questions]}")
            print(f"Debug - status: {status}")
            
            # 問題数制限を適用
            if num_questions != 'all' and len(questions) > num_questions:
                questions = random.sample(questions, num_questions)
                questions.sort(key=lambda x: x.question_number)
            
            # POSTリクエストがある場合のみ回答処理を実行
            if request.method == 'POST':
                # POSTされたquestion_idをすべて取得
                post_question_ids = [
                    int(key.replace('answer_', ''))
                    for key in request.POST.keys()
                    if key.startswith('answer_')
                ]
                
                # 既存の回答を削除（POSTされたquestion_idのみ）
                UserAnswer.objects.filter(
                    user=request.user,
                    question_id__in=post_question_ids
                ).delete()
                
                # 回答を保存
                for question_id in post_question_ids:
                    answer_key = f'answer_{question_id}'
                    selected_choice_id = request.POST.get(answer_key)
                    if selected_choice_id:
                        choice = Choice.objects.get(id=selected_choice_id)
                        is_correct = choice.is_correct
                        question = Question.objects.get(id=question_id)
                        UserAnswer.objects.create(
                            user=request.user,
                            question=question,
                            selected_choice=choice,
                            is_correct=is_correct
                        )
                        # 進捗を更新
                        update_user_progress(request.user, level, question_type, is_correct)

                # 今回回答したquestion_idと出題順序をセッションに保存
                request.session[f'answered_questions_{question_type}_{level}'] = post_question_ids

                return redirect('exams:answer_results', level=level, question_type=question_type)
            
            # GETリクエストの場合は問題を表示
            # 問題と回答を組み合わせる
            questions_with_answers = []
            for question in questions:
                choices = Choice.objects.filter(question=question).order_by('order')
                correct_choice = choices.filter(is_correct=True).first()
                user_answer = user_answer_dict.get(question.id)
                
                questions_with_answers.append({
                    'question': question,
                    'choices': choices,
                    'user_answer': user_answer.selected_choice if user_answer else None,
                    'is_correct': user_answer.is_correct if user_answer else None,
                    'correct_choice': correct_choice,
                    'explanation': question.explanation
                })
            
            context = {
                'level': level,
                'question_type': question_type,
                'question_type_display': question_types.get(question_type, ''),
                'num_questions': num_questions,
                'status': status,
                'questions': questions_with_answers,
                'question_count_options': question_count_options,
            }
            return render(request, 'exams/question_list.html', context)

@login_required
def answer_results(request, level, question_type):
    if question_type == 'random':
        # ランダム10問の場合
        # セッションから今回回答したquestion_idを取得
        session_key = f'answered_questions_{question_type}_{level}'
        answered_question_ids = request.session.get(session_key, [])
        
        # 各問題のタイプを判定して適切な回答を取得
        answers_with_questions = []
        
        for question_id in answered_question_ids:
            # リスニングイラスト問題かどうかを判定
            try:
                answer = ListeningUserAnswer.objects.get(
                    user=request.user,
                    question_id=question_id
                )
                choices = ListeningChoice.objects.filter(question=answer.question).order_by('order')
                answers_with_questions.append({
                    'question': answer.question,
                    'choices': choices,
                    'user_answer': answer.selected_answer,
                    'is_correct': answer.is_correct,
                    'correct_answer': answer.question.correct_answer,
                    'explanation': getattr(answer.question, 'explanation', ''),
                    'category': 'listening_illustration',
                    'order': answered_question_ids.index(question_id)
                })
            except ListeningUserAnswer.DoesNotExist:
                # 通常の問題の場合
                try:
                    answer = UserAnswer.objects.get(
                        user=request.user,
                        question_id=question_id
                    )
                    choices = Choice.objects.filter(question=answer.question).order_by('order')
                    correct_choice = choices.filter(is_correct=True).first()
                    answers_with_questions.append({
                        'question': answer.question,
                        'choices': choices,
                        'user_answer': answer.selected_choice,
                        'is_correct': answer.is_correct,
                        'correct_choice': correct_choice,
                        'explanation': answer.question.explanation,
                        'category': answer.question.question_type,
                        'order': answered_question_ids.index(question_id)
                    })
                except UserAnswer.DoesNotExist:
                    continue
        
        # 出題順序でソート
        answers_with_questions.sort(key=lambda x: x['order'])
        
        # 正解数を計算
        correct_count = sum(1 for answer in answers_with_questions if answer['is_correct'])
        total_count = len(answers_with_questions)
        
        context = {
            'level': level,
            'question_type': question_type,
            'answers_with_questions': answers_with_questions,
            'correct_count': correct_count,
            'total_count': total_count,
        }
        return render(request, 'exams/answer_results.html', context)
    
    elif question_type == 'listening_illustration':
        # イラスト問題の場合
        # セッションから今回回答したquestion_idを取得
        session_key = f'answered_questions_{question_type}_{level}'
        answered_question_ids = request.session.get(session_key, [])
        
        print(f"Debug - Listening Illustration answered_question_ids: {answered_question_ids}")
        
        # 今回回答したquestion_idのListeningUserAnswerのみを取得
        user_answers = ListeningUserAnswer.objects.filter(
            user=request.user,
            question_id__in=answered_question_ids
        ).select_related('question')
        
        # 出題順序に従ってソート
        # answered_question_idsの順序でソートする辞書を作成
        order_dict = {question_id: index for index, question_id in enumerate(answered_question_ids)}
        
        # 問題と回答を組み合わせる（出題順序でソート）
        answers_with_questions = []
        for answer in user_answers:
            choices = ListeningChoice.objects.filter(question=answer.question).order_by('order')
            answers_with_questions.append({
                'question': answer.question,
                'choices': choices,
                'user_answer': answer.selected_answer,
                'is_correct': answer.is_correct,
                'correct_answer': answer.question.correct_answer,
                'explanation': getattr(answer.question, 'explanation', ''),
                'order': order_dict.get(answer.question.id, 0)  # 出題順序を追加
            })
        
        # 出題順序でソート
        answers_with_questions.sort(key=lambda x: x['order'])
        
        # 正解数を計算
        correct_count = sum(1 for answer in user_answers if answer.is_correct)
        total_count = len(user_answers)
        
        context = {
            'level': level,
            'question_type': question_type,
            'answers_with_questions': answers_with_questions,
            'correct_count': correct_count,
            'total_count': total_count,
        }
        return render(request, 'exams/answer_results.html', context)
    
    elif question_type in ['listening_conversation', 'listening_passage']:
        # その他のリスニング問題の場合
        # セッションから今回回答したquestion_idを取得
        session_key = f'answered_questions_{question_type}_{level}'
        answered_question_ids = request.session.get(session_key, [])
        
        # 今回回答したquestion_idのUserAnswerのみを取得
        user_answers = UserAnswer.objects.filter(
            user=request.user,
            question_id__in=answered_question_ids
        ).select_related('question')
        
        # 出題順序に従ってソート
        # answered_question_idsの順序でソートする辞書を作成
        order_dict = {question_id: index for index, question_id in enumerate(answered_question_ids)}
        
        # 問題と回答を組み合わせる（出題順序でソート）
        answers_with_questions = []
        for answer in user_answers:
            choices = Choice.objects.filter(question=answer.question).order_by('order')
            correct_choice = choices.filter(is_correct=True).first()
            answers_with_questions.append({
                'question': answer.question,
                'choices': choices,
                'user_answer': answer.selected_choice,
                'is_correct': answer.is_correct,
                'correct_choice': correct_choice,
                'explanation': answer.question.explanation,
                'order': order_dict.get(answer.question.id, 0)  # 出題順序を追加
            })
        
        # 出題順序でソート
        answers_with_questions.sort(key=lambda x: x['order'])
        
        # 正解数を計算
        correct_count = sum(1 for answer in user_answers if answer.is_correct)
        total_count = len(user_answers)
        
        context = {
            'level': level,
            'question_type': question_type,
            'answers_with_questions': answers_with_questions,
            'correct_count': correct_count,
            'total_count': total_count,
        }
        return render(request, 'exams/answer_results.html', context)
    
    elif question_type == 'reading_comprehension':
        # 長文読解問題の場合
        # セッションから今回回答したquestion_idを取得
        session_key = f'answered_questions_{question_type}_{level}'
        answered_question_ids = request.session.get(session_key, [])
        
        # パッセージの順序を取得
        passage_order_key = f'passage_order_{question_type}_{level}'
        passage_order = request.session.get(passage_order_key, {})
        
        print(f"Debug - answered_question_ids: {answered_question_ids}")
        print(f"Debug - passage_order: {passage_order}")
        
        # 今回回答したquestion_idのReadingUserAnswerのみを取得
        user_answers = ReadingUserAnswer.objects.filter(
            user=request.user,
            reading_question_id__in=answered_question_ids
        ).select_related('reading_question', 'reading_question__passage')
        
        # 出題順序に従ってソート
        # answered_question_idsの順序でソートする辞書を作成
        order_dict = {question_id: index for index, question_id in enumerate(answered_question_ids)}
        
        # パッセージごとに問題と回答をグループ化（出題順序でソート）
        passages_with_answers = {}
        for answer in user_answers:
            passage = answer.reading_question.passage
            if passage not in passages_with_answers:
                passages_with_answers[passage] = []
            
            choices = ReadingChoice.objects.filter(question=answer.reading_question).order_by('order')
            correct_choice = choices.filter(is_correct=True).first()
            passages_with_answers[passage].append({
                'question': answer.reading_question,
                'choices': choices,
                'user_answer': answer.selected_reading_choice,
                'is_correct': answer.is_correct,
                'correct_choice': correct_choice,
                'explanation': getattr(answer.reading_question, 'explanation', ''),
                'order': order_dict.get(answer.reading_question.id, 0)  # 出題順序を追加
            })
        
        print(f"Debug - passages_with_answers keys: {[p.id for p in passages_with_answers.keys()]}")
        
        # 各パッセージ内で出題順序でソート
        for passage in passages_with_answers:
            passages_with_answers[passage].sort(key=lambda x: x['order'])
        
        # パッセージを順序でソート
        sorted_passages = sorted(passages_with_answers.items(), key=lambda x: passage_order.get(str(x[0].id), 999))
        passages_with_answers = dict(sorted_passages)
        
        print(f"Debug - sorted passages: {[p.id for p in passages_with_answers.keys()]}")
        
        # 正解数を計算
        correct_count = sum(1 for answer in user_answers if answer.is_correct)
        total_count = len(user_answers)
        
        context = {
            'level': level,
            'question_type': question_type,
            'passages_with_answers': passages_with_answers,
            'correct_count': correct_count,
            'total_count': total_count,
        }
        return render(request, 'exams/answer_results.html', context)
    
    else:
        # 通常の問題の場合
        # セッションから今回回答したquestion_idを取得
        session_key = f'answered_questions_{question_type}_{level}'
        answered_question_ids = request.session.get(session_key, [])
        
        # 今回回答したquestion_idのUserAnswerのみを取得
        user_answers = UserAnswer.objects.filter(
            user=request.user,
            question_id__in=answered_question_ids
        ).select_related('question')
        
        # 出題順序に従ってソート
        # answered_question_idsの順序でソートする辞書を作成
        order_dict = {question_id: index for index, question_id in enumerate(answered_question_ids)}
        
        # 問題と回答を組み合わせる（出題順序でソート）
        answers_with_questions = []
        for answer in user_answers:
            choices = Choice.objects.filter(question=answer.question).order_by('order')
            correct_choice = choices.filter(is_correct=True).first()
            answers_with_questions.append({
                'question': answer.question,
                'choices': choices,
                'user_answer': answer.selected_choice,
                'is_correct': answer.is_correct,
                'correct_choice': correct_choice,
                'explanation': answer.question.explanation,
                'order': order_dict.get(answer.question.id, 0)  # 出題順序を追加
            })
        
        # 出題順序でソート
        answers_with_questions.sort(key=lambda x: x['order'])
    
        # 正解数を計算
        correct_count = sum(1 for answer in user_answers if answer.is_correct)
        total_count = len(user_answers)
        
        context = {
            'level': level,
            'question_type': question_type,
            'answers_with_questions': answers_with_questions,
            'correct_count': correct_count,
            'total_count': total_count,
        }
        return render(request, 'exams/answer_results.html', context)

@login_required
def progress_view(request):
    """学習進捗を表示"""
    user = request.user
    levels = Question.objects.values_list('level', flat=True).distinct()
    
    # 各級の進捗を取得
    progress_data = {}
    for level in levels:
        level_progress = UserProgress.objects.filter(user=user, level=level)
        progress_data[level] = {
            'grammar_fill': progress_to_dict(level_progress.filter(question_type='grammar_fill').first()),
            'conversation_fill': progress_to_dict(level_progress.filter(question_type='conversation_fill').first()),
            'word_order': progress_to_dict(level_progress.filter(question_type='word_order').first()),
            'reading_comprehension': progress_to_dict(level_progress.filter(question_type='reading_comprehension').first()),
            'listening_illustration': progress_to_dict(level_progress.filter(question_type='listening_illustration').first()),
            'listening_conversation': progress_to_dict(level_progress.filter(question_type='listening_conversation').first()),
            'listening_passage': progress_to_dict(level_progress.filter(question_type='listening_passage').first()),
        }
        
        # デバッグ出力を追加
        print(f"Debug - Progress data for level {level}:")
        for question_type, progress in progress_data[level].items():
            print(f"  {question_type}: last_attempted={progress['last_attempted']}")
    
    return render(request, 'exams/progress.html', {
        'progress_data': progress_data,
        'levels': levels,
        'progress_json': json.dumps(progress_data)
    })

def update_user_progress(user, level, question_type, is_correct):
    """ユーザーの進捗を更新"""
    progress, created = UserProgress.objects.get_or_create(
        user=user,
        level=level,
        question_type=question_type,
        defaults={
            'total_attempts': 0,
            'correct_answers': 0,
            'last_attempted': timezone.now()
        }
    )
    print(f"Debug - Updating progress for user={user.username}, level={level}, type={question_type}, is_correct={is_correct}")
    print(f"Debug - Before update: last_attempted={progress.last_attempted}")
    progress.update_progress(is_correct)
    print(f"Debug - After update: last_attempted={progress.last_attempted}")

def progress_to_dict(progress):
    """進捗オブジェクトを辞書に変換"""
    if progress is None:
        print(f"Debug - progress_to_dict: progress is None")
        return {
            'accuracy_rate': 0,
            'total_attempts': 0,
            'correct_answers': 0,
            'last_attempted': None
        }
    print(f"Debug - progress_to_dict: progress.last_attempted={progress.last_attempted}")
    result = {
        'accuracy_rate': progress.accuracy_rate,
        'total_attempts': progress.total_attempts,
        'correct_answers': progress.correct_answers,
        'last_attempted': progress.last_attempted  # 日付オブジェクトをそのまま返す
    }
    print(f"Debug - progress_to_dict: result.last_attempted={result['last_attempted']}")
    return result

@login_required
def clear_progress(request):
    """学習進捗をクリア"""
    if request.method == 'POST':
        user = request.user
        # ユーザーの全ての進捗をクリア
        UserProgress.objects.filter(user=user).delete()
        # ユーザーの全ての回答履歴をクリア
        UserAnswer.objects.filter(user=user).delete()
        messages.success(request, '学習進捗をクリアしました。')
    return redirect('exams:progress')

@login_required
def feedback_form(request):
    """フィードバックフォームを表示・処理"""
    if request.method == 'POST':
        from .forms import FeedbackForm
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'フィードバックを送信しました。ありがとうございます。')
            return redirect('exams:exam_list')
    else:
        from .forms import FeedbackForm
        form = FeedbackForm()
    
    return render(request, 'exams/feedback_form.html', {'form': form})
