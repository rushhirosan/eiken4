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
    num_questions = int(request.GET.get('num_questions', 10))
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
    }
    
    # 問題数のオプション
    question_count_options = {
        3: '3問',
        5: '5問',
        10: '10問',
        20: '20問',
        30: '30問',
    }
    
    if question_type == 'listening_illustration':
        # イラスト問題の場合
        questions = ListeningQuestion.objects.filter(level=level).order_by('id')
        print(f"Debug - Listening Illustration Questions: {questions.count()}")  # デバッグ出力
        
        if len(questions) > num_questions:
            questions = random.sample(list(questions), num_questions)
            questions.sort(key=lambda x: x.id)
        
        # ユーザーの回答を取得
        user_answers = {}
        answers = ListeningUserAnswer.objects.filter(
            user=request.user,
            question__in=questions
        )
        for answer in answers:
            user_answers[answer.question.id] = answer.selected_answer
        
        # 問題と選択肢を組み合わせる
        questions_with_choices = []
        for question in questions:
            choices = ListeningChoice.objects.filter(question=question).order_by('order')
            questions_with_choices.append({
                'question': question,
                'choices': choices,
                'user_answer': user_answers.get(question.id),
                'is_correct': user_answers.get(question.id) == question.correct_answer if question.id in user_answers else None,
                'explanation': question.explanation
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
        # その他のリスニング問題の場合
        questions = Question.objects.filter(
            level=level,
            question_type=question_type
        ).order_by('id')
        print(f"Debug - Listening Questions: {questions.count()}")  # デバッグ出力
        
        if len(questions) > num_questions:
            questions = random.sample(list(questions), num_questions)
            questions.sort(key=lambda x: x.id)
        
        # ユーザーの回答を取得
        user_answers = {}
        answers = UserAnswer.objects.filter(
            user=request.user,
            question__in=questions
        )
        for answer in answers:
            user_answers[answer.question.id] = answer.selected_choice
        
        # 問題と回答を組み合わせる
        questions_with_answers = []
        for question in questions:
            choices = Choice.objects.filter(question=question).order_by('order')
            correct_choice = choices.filter(is_correct=True).first()
            questions_with_answers.append({
                'question': question,
                'choices': choices,
                'user_answer': user_answers.get(question.id),
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
        passages = ReadingPassage.objects.filter(level=level).order_by('id')
        print(f"Debug - Reading Passages: {passages.count()}")  # デバッグ出力
        
        # パッセージと問題を組み合わせる
        passages_with_questions = []
        for passage in passages:
            passage_questions = ReadingQuestion.objects.filter(passage=passage).order_by('question_number')
            
            # 問題数を制限（ランダムに選択）
            if len(passage_questions) > num_questions:
                passage_questions = random.sample(list(passage_questions), num_questions)
                passage_questions.sort(key=lambda x: x.question_number)
            
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
        if len(questions) > num_questions:
            questions = random.sample(questions, num_questions)
            questions.sort(key=lambda x: x.question_number)
        
        # ユーザーの回答を取得
        user_answers = {}
        answers = UserAnswer.objects.filter(
            user=request.user,
            question__in=questions
        )
        for answer in answers:
            user_answers[answer.question.id] = answer.selected_choice
        
        # 問題と回答を組み合わせる
        questions_with_answers = []
        for question in questions:
            choices = Choice.objects.filter(question=question).order_by('order')
            correct_choice = choices.filter(is_correct=True).first()
            questions_with_answers.append({
                'question': question,
                'choices': choices,
                'user_answer': user_answers.get(question.id),
                'correct_choice': correct_choice,
                'explanation': question.explanation
            })
        
        print(f"Debug - Questions with answers: {len(questions_with_answers)}")  # デバッグ出力
        for q in questions_with_answers:
            print(f"Debug - Question: {q['question'].question_text}")  # デバッグ出力
            print(f"Debug - Choices: {[c.choice_text for c in q['choices']]}")  # デバッグ出力
        
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
                
            except (ReadingQuestion.DoesNotExist, ReadingChoice.DoesNotExist):
                messages.error(request, f'問題 {question_id} の選択肢が見つかりませんでした。')
                continue
        
        messages.success(request, '回答を保存しました。')
        return redirect('exams:answer_results', level=level, type='reading_comprehension')
    
    return redirect('exams:question_list', level=level, type='reading_comprehension')

@login_required
def submit_answers(request):
    if request.method == 'POST':
        question_type = request.POST.get('question_type')
        level = int(request.POST.get('level'))
        num_questions = int(request.POST.get('num_questions', 10))
        
        if question_type == 'listening_illustration':
            # イラスト問題の場合
            questions = ListeningQuestion.objects.filter(level=level).order_by('id')
            if len(questions) > num_questions:
                questions = random.sample(list(questions), num_questions)
                questions.sort(key=lambda x: x.id)
        
        # 既存の回答を削除
            ListeningUserAnswer.objects.filter(
            user=request.user,
                question__in=questions
        ).delete()
        
            # 回答を保存
            for question in questions:
                answer_key = f'answer_{question.id}'
                if answer_key in request.POST:
                    selected_answer = request.POST.get(answer_key)
                    is_correct = selected_answer == question.correct_answer
                    ListeningUserAnswer.objects.create(
                        user=request.user,
                        question=question,
                        selected_answer=selected_answer,
                        is_correct=is_correct
                    )
            
            return redirect('exams:answer_results', level=level, type=question_type)
        
        elif question_type in ['listening_conversation', 'listening_passage']:
            # その他のリスニング問題の場合
            questions = Question.objects.filter(
                level=level,
                question_type=question_type
            ).order_by('id')
            
            if len(questions) > num_questions:
                questions = random.sample(list(questions), num_questions)
                questions.sort(key=lambda x: x.id)
            
            # 既存の回答を削除
            UserAnswer.objects.filter(
                user=request.user,
                question__in=questions
            ).delete()
                
                # 回答を保存
            for question in questions:
                answer_key = f'answer_{question.id}'
                if answer_key in request.POST:
                    selected_choice = request.POST.get(answer_key)
                    choice = Choice.objects.get(id=selected_choice)
                    is_correct = choice.is_correct
                UserAnswer.objects.create(
                    user=request.user,
                    question=question,
                        selected_choice=selected_choice,
                    is_correct=is_correct
                )
                
            return redirect('exams:answer_results', level=level, type=question_type)
        
        elif question_type == 'reading_comprehension':
            # 長文読解問題の場合
            passages = ReadingPassage.objects.filter(level=level).order_by('id')
            
            # パッセージごとに問題を処理
            for passage in passages:
                passage_questions = ReadingQuestion.objects.filter(passage=passage).order_by('question_number')
                
                # 問題数を制限
                if len(passage_questions) > num_questions:
                    passage_questions = random.sample(list(passage_questions), num_questions)
                    passage_questions.sort(key=lambda x: x.question_number)
                
                # 既存の回答を削除
                ReadingUserAnswer.objects.filter(
                    user=request.user,
                    reading_question__in=passage_questions
                ).delete()
                
                # 回答を保存
                for question in passage_questions:
                    answer_key = f'answer_{question.id}'
                    if answer_key in request.POST:
                        selected_choice = request.POST.get(answer_key)
                        choice = ReadingChoice.objects.get(id=selected_choice)
                        is_correct = choice.is_correct
                        ReadingUserAnswer.objects.create(
                            user=request.user,
                            reading_question=question,
                            selected_reading_choice=selected_choice,
                            is_correct=is_correct
                        )
            
            return redirect('exams:answer_results', level=level, type=question_type)
        
        else:
            # 通常の問題の場合
            questions = Question.objects.filter(level=level, question_type=question_type).order_by('question_number')
            questions = list(questions)
            if len(questions) > num_questions:
                questions = random.sample(questions, num_questions)
                questions.sort(key=lambda x: x.question_number)
            
            # 既存の回答を削除
            UserAnswer.objects.filter(
                user=request.user,
                question__in=questions
            ).delete()
            
            # 回答を保存
            for question in questions:
                answer_key = f'answer_{question.id}'
                if answer_key in request.POST:
                    selected_choice = request.POST.get(answer_key)
                    choice = Choice.objects.get(id=selected_choice)
                    is_correct = choice.is_correct
                    UserAnswer.objects.create(
                        user=request.user,
                        question=question,
                        selected_choice=selected_choice,
                        is_correct=is_correct
                    )
        
        return redirect('exams:answer_results', level=level, type=question_type)
    
    return redirect('exams:question_list', level=1)

@login_required
def answer_results(request, level, question_type):
    if question_type == 'listening_illustration':
        # イラスト問題の場合
        user_answers = ListeningUserAnswer.objects.filter(
            user=request.user,
            question__level=level
        ).select_related('question')
        
        # 問題と回答を組み合わせる
        answers_with_questions = []
        for answer in user_answers:
            choices = ListeningChoice.objects.filter(question=answer.question).order_by('order')
            answers_with_questions.append({
                'question': answer.question,
                'choices': choices,
                'user_answer': answer.selected_answer,
                'is_correct': answer.is_correct,
                'correct_answer': answer.question.correct_answer
            })
        
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
        user_answers = UserAnswer.objects.filter(
            user=request.user,
            question__level=level,
            question__question_type=question_type
        ).select_related('question')
        
        # 問題と回答を組み合わせる
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
                'explanation': answer.question.explanation
            })
        
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
        user_answers = ReadingUserAnswer.objects.filter(
            user=request.user,
            reading_question__passage__level=level
        ).select_related('reading_question', 'reading_question__passage')
        
        # パッセージごとに問題と回答をグループ化
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
                'explanation': getattr(answer.reading_question, 'explanation', '')
            })
        
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
        user_answers = UserAnswer.objects.filter(
            user=request.user,
            question__level=level,
            question__question_type=question_type
        ).select_related('question')
        
        # 問題と回答を組み合わせる
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
                'explanation': answer.question.explanation
            })
        
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
        }
    
    return render(request, 'exams/progress.html', {
        'progress_data': progress_data,
        'levels': levels,
        'progress_json': json.dumps(progress_data)
    })

def progress_to_dict(progress):
    """進捗オブジェクトを辞書に変換"""
    if progress is None:
        return {
            'accuracy_rate': 0,
            'total_attempts': 0,
            'correct_answers': 0,
            'last_attempted': None
        }
    return {
        'accuracy_rate': progress.accuracy_rate,
        'total_attempts': progress.total_attempts,
        'correct_answers': progress.correct_answers,
        'last_attempted': progress.last_attempted.strftime('%Y/%m/%d') if progress.last_attempted else None
    }

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
