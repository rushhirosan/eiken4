from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from accounts.views import get_client_ip
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.utils import timezone
from django.template.loader import render_to_string
from django.urls import reverse
from .models import (
    Question,
    Choice,
    UserAnswer,
    UserProgress,
    ReadingUserAnswer,
    DailyProgress,
    Feedback,
    WritingUserAnswer,
)
from django.db.models import Count, Q
import random
import re
from django.http import JsonResponse
from django.contrib import messages
import json
from questions.models import ReadingPassage, ReadingQuestion, ReadingChoice, ListeningQuestion, ListeningUserAnswer, ListeningChoice
from django.urls import reverse
from django.utils import timezone
import logging
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

from .gamification import (
    MOCK_EXAM_UNLOCK_MIN_RATE,
    RANDOM_UNLOCK_MIN_RATE,
    RANDOM_UNLOCK_REQUIRED_CATEGORIES,
    build_adventure_summary,
    build_badge_collection,
    build_daily_missions,
    build_habit_summary,
    build_session_achievements,
    enrich_foundation_progress,
    get_daily_mission_goal,
    pop_pre_submit_unlock_snapshot,
    process_gamification_after_session,
    random_scope_description,
    random_unlock_help_text,
    set_daily_mission_goal,
    store_pre_submit_unlock_snapshot,
)
from .writing_feedback import analyze_writing_response, get_writing_rubric
from .choice_shuffle import (
    apply_choice_shuffle_to_items,
    apply_choice_shuffle_to_passages,
    order_choices_for_display,
)


def _format_objective_explanation(raw_explanation, correct_choice):
    """4級表示に寄せるため、機械的な解説文は最小限の実用文に整形する。"""
    explanation = (raw_explanation or "").strip()
    if not explanation:
        return ""
    if re.search(r"公式.*解答.*基づく", explanation):
        correct_text = correct_choice.choice_text if correct_choice else ""
        if correct_text:
            return (
                f"正解は「{correct_text}」です。文脈に最も合う語句を選びます。\n\n"
                "※ 公式一次試験の解答に基づいています。"
            )
        return "文脈に最も合う語句を選ぶ問題です。※ 公式一次試験の解答に基づいています。"
    return explanation


def _is_currently_correct_choice(selected_choice):
    """保存時の採点結果ではなく、現在の選択肢定義で正誤を判定する。"""
    return bool(selected_choice and selected_choice.is_correct)


def _has_submittable_answers(post):
    """POSTに空でない回答が1件以上含まれるか。"""
    for key, value in post.items():
        if key.startswith('answer_') and (value or '').strip():
            return True
    return False


def _redirect_empty_submission(request, level, question_type):
    status = request.POST.get('status', 'unanswered')
    num_questions = request.POST.get('num_questions', '5')
    messages.warning(
        request,
        '回答する問題がありません。状態または問題数を変更してください。',
    )
    url = reverse('exams:question_list_by_level', kwargs={'level': level})
    return redirect(f'{url}?type={question_type}&status={status}&num_questions={num_questions}')

FOUNDATION_QUESTION_TYPES = [
    'grammar_fill',
    'conversation_fill',
    'word_order',
    'reading_comprehension',
    'listening_illustration',
    'listening_conversation',
    'listening_passage',
]

from .listening_utils import (
    LISTENING_ILLUSTRATION_PART1_MAX,
    LISTENING_ILLUSTRATION_PART3_MIN,
    filter_listening_illustrations,
    listening_illustration_number,
)
EXAM_LEVEL_ENTRIES = [
    ('5', '英検5級'),
    ('4', '英検4級'),
    ('3', '英検3級'),
]
VALID_EXAM_LEVELS = {code for code, _ in EXAM_LEVEL_ENTRIES}
QUESTION_TYPE_LABELS = {
    'grammar_fill': '文法・語彙問題',
    'conversation_fill': '会話補充問題',
    'word_order': '語順選択問題',
    'reading_comprehension': '長文読解問題',
    'writing': 'ライティング問題',
    'listening_illustration': 'リスニング第1部: イラスト問題',
    'listening_illustration_part3': 'リスニング第3部: イラスト一致問題',
    'listening_conversation': 'リスニング第2部: 会話問題',
    'listening_passage': 'リスニング第3部: 文章問題',
}

PREFERRED_LEVEL_SESSION_KEY = 'preferred_exam_level'


def _foundation_question_types_for_level(level):
    level = str(level)
    if level == '5':
        return [
            'grammar_fill',
            'conversation_fill',
            'word_order',
            'listening_illustration',
            'listening_conversation',
            'listening_illustration_part3',
        ]
    if level == '3':
        return [
            'grammar_fill',
            'conversation_fill',
            'reading_comprehension',
            'writing',
            'listening_illustration',
            'listening_conversation',
            'listening_passage',
        ]
    return list(FOUNDATION_QUESTION_TYPES)


_filter_listening_illustrations = filter_listening_illustrations
_listening_illustration_number = listening_illustration_number


def _random_categories_for_level(level):
    level = str(level)
    categories = [
        ('grammar_fill', Question),
        ('conversation_fill', Question),
    ]
    if level != '3':
        categories.append(('word_order', Question))
    categories.append(('listening_conversation', Question))
    if level == '4':
        categories.append(('listening_passage', Question))
    categories.append(('listening_illustration', ListeningQuestion))
    return categories


def _get_mock_exam_structure(level):
    level = str(level)
    if level == '5':
        return [
            ('grammar_fill', Question, 15),
            ('conversation_fill', Question, 5),
            ('word_order', Question, 5),
            ('listening_illustration_part1', ListeningQuestion, 10),
            ('listening_conversation', Question, 5),
            ('listening_illustration_part3', ListeningQuestion, 10),
        ]
    return [
        ('grammar_fill', Question, 15),
        ('conversation_fill', Question, 5),
        ('word_order', Question, 5),
        ('reading_comprehension', ReadingPassage, 3),
        ('listening_illustration', ListeningQuestion, 10),
        ('listening_conversation', Question, 10),
        ('listening_passage', Question, 10),
    ]


def _is_level5_only_type(level, question_type):
    if str(level) != '5':
        return False
    return question_type in ('reading_comprehension', 'writing', 'listening_passage')


def _is_correct_listening_illustration_answer(question, selected_answer, request=None, level=None):
    """リスニング第1部の回答値（テキスト/番号）から正解判定を行う。"""
    normalized_answer = (selected_answer or '').strip()
    choices = list(ListeningChoice.objects.filter(question=question).order_by('order', 'id'))
    if request is not None and level is not None:
        choices = order_choices_for_display(
            request,
            level,
            'listening_illustration',
            question.id,
            choices,
            create_if_missing=False,
        )
    if not normalized_answer or not choices:
        return False

    # choice_text が空白混じりでも一致できるよう Python 側で正規化して判定
    for choice in choices:
        if normalized_answer == (choice.choice_text or '').strip():
            return choice.is_correct

    # 互換性: 番号回答（"1" など）なら order と画面上の並び（1始まり）の双方で判定
    if normalized_answer.isdigit():
        answer_number = int(normalized_answer)

        selected_choice = next((c for c in choices if c.order == answer_number), None)
        if selected_choice:
            return selected_choice.is_correct

        index_based = answer_number - 1
        if 0 <= index_based < len(choices):
            return choices[index_based].is_correct

    # フォールバック: correct_answer が番号/テキストどちらでも判定可能にする
    normalized_correct_answer = str(question.correct_answer or '').strip()
    if normalized_correct_answer:
        if normalized_answer == normalized_correct_answer:
            return True
        if normalized_correct_answer.isdigit():
            correct_number = int(normalized_correct_answer)
            return normalized_answer.isdigit() and int(normalized_answer) == correct_number

    return False


def _set_preferred_exam_level(request, level):
    level = str(level)
    if level in VALID_EXAM_LEVELS:
        request.session[PREFERRED_LEVEL_SESSION_KEY] = level


def _get_preferred_exam_level(request):
    level = request.session.get(PREFERRED_LEVEL_SESSION_KEY, '4')
    return level if level in VALID_EXAM_LEVELS else '4'


def _exam_level_name(level_code):
    return dict(EXAM_LEVEL_ENTRIES).get(level_code, f'英検{level_code}級')


def _extra_display_progress(user, level_code, foundation_progress):
    """UI-only progress rows (e.g. 3級ライティングは解放条件外だが進捗は表示)."""
    if str(level_code) != '3':
        return []
    if any(item['question_type'] == 'writing' for item in foundation_progress):
        return []
    total_questions = _total_questions_for_type(level_code, 'writing')
    if total_questions <= 0:
        return []
    return [{
        'question_type': 'writing',
        'display_name': QUESTION_TYPE_LABELS.get('writing', 'writing'),
        'progress_rate': _progress_rate_for_type(user, level_code, 'writing'),
        'total_questions': total_questions,
        'counts_toward_mock': False,
    }]


def _build_exam_section(user, level_code, level_name, daily_goal=3):
    question_types = {
        'grammar_fill': '文法・語彙問題',
        'conversation_fill': '会話補充問題',
        'word_order': '語順選択問題',
        'reading_comprehension': '長文読解問題',
        'writing': 'ライティング問題',
        'listening_conversation': 'リスニング第2部: 会話問題',
        'listening_illustration': 'リスニング第1部: イラスト問題',
        'listening_passage': 'リスニング第3部: 文章問題',
        'random': 'ランダム10問',
        'mock_exam': '模擬試験問題',
    }
    question_counts = {
        q_type: _total_questions_for_type(level_code, q_type)
        for q_type in question_types.keys()
    }
    if str(level_code) == '5':
        question_counts['listening_illustration_part3'] = _total_questions_for_type(
            level_code, 'listening_illustration_part3'
        )
        question_counts['listening_illustration'] = _total_questions_for_type(
            level_code, 'listening_illustration'
        )
    unlock_status = _build_exam_unlock_status(user, level_code)
    foundation_rows = (
        unlock_status.get('foundation_progress', [])
        + _extra_display_progress(user, level_code, unlock_status.get('foundation_progress', []))
    )
    foundation_progress = enrich_foundation_progress(foundation_rows)
    progress_by_type = {
        item['question_type']: item for item in foundation_progress
    }
    daily_missions = build_daily_missions(
        user=user,
        level=level_code,
        unlock_status=unlock_status,
        foundation_progress_by_type=progress_by_type,
        daily_goal=daily_goal,
    )
    return {
        'level_code': level_code,
        'level_name': level_name,
        'question_counts': question_counts,
        'unlock_status': unlock_status,
        'adventure_summary': build_adventure_summary(unlock_status),
        'foundation_progress_by_type': progress_by_type,
        'daily_missions': daily_missions,
        'habit_summary': build_habit_summary(user, level=level_code),
        'badge_collection': build_badge_collection(user, level=level_code),
        'random_scope_description': random_scope_description(level_code),
        'random_unlock_help_text': random_unlock_help_text(),
    }


@login_required
def exam_list(request):
    """試験一覧を表示（選択中の級にフォーカス）"""
    level_param = request.GET.get('level')
    if level_param in VALID_EXAM_LEVELS:
        active_level = level_param
        _set_preferred_exam_level(request, active_level)
    else:
        active_level = _get_preferred_exam_level(request)

    daily_goal_param = request.GET.get('daily_goal')
    if daily_goal_param is not None:
        set_daily_mission_goal(request, daily_goal_param, level=active_level)
    daily_goal = get_daily_mission_goal(request, level=active_level)

    active_name = _exam_level_name(active_level)
    other_levels = [
        {'code': code, 'name': name}
        for code, name in EXAM_LEVEL_ENTRIES
        if code != active_level
    ]

    context = {
        'active_section': _build_exam_section(
            request.user,
            active_level,
            active_name,
            daily_goal=daily_goal,
        ),
        'other_levels': other_levels,
    }

    return render(request, 'exams/exam_list.html', context)

@login_required
def question_list(request, level=None, exam_id=None):
    if level is not None:
        _set_preferred_exam_level(request, level)

    question_type = request.GET.get('type')
    
    # デバッグ出力を追加
    logger.debug(f"Debug - question_list called with level={level}, exam_id={exam_id}, question_type={question_type}")
    logger.debug(f"Debug - request.GET: {request.GET}")
    logger.debug(f"Debug - request.path: {request.path}")
    
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
    
    status = request.GET.get('status', 'unanswered')

    if question_type == 'writing' and str(level) != '3':
        messages.info(request, 'ライティング問題は英検3級のみです。')
        return redirect('exams:exam_list')

    if _is_level5_only_type(level, question_type):
        messages.info(request, 'この問題形式は英検5級にはありません。')
        return redirect('exams:exam_list')
    
    logger.debug(f"Debug - Level: {level}, Question Type: {question_type}")  # デバッグ出力
    
    # 問題タイプの定義
    question_types = {
        'grammar_fill': '文法・語彙問題',
        'conversation_fill': '会話補充問題',
        'word_order': '語順選択問題',
        'reading_comprehension': '長文読解問題',
        'writing': 'ライティング問題',
        'listening_conversation': 'リスニング第2部: 会話問題',
        'listening_illustration': 'リスニング第1部: イラスト問題',
        'listening_illustration_part3': 'リスニング第3部: イラスト一致問題',
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
    
    # 長文読解・ライティングは1問から選べる
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
    elif question_type == 'writing':
        question_count_options = {
            1: '1問',
            3: '3問',
            5: '5問',
            10: '10問',
            20: '20問',
            30: '30問',
            'all': '全て',
        }
    
    if question_type == 'random':
        unlock_status = _build_exam_unlock_status(request.user, str(level))
        if not unlock_status['random']['is_unlocked']:
            messages.warning(
                request,
                f'ランダム10問は、{random_unlock_help_text()}になると解放されます。',
            )
            return redirect('exams:exam_list')

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
        categories = _random_categories_for_level(level)
        
        # 各カテゴリーから2問ずつ取得（合計12問、その後10問に絞る）
        for category_type, model_class in categories:
            if model_class == ListeningQuestion:
                questions = model_class.objects.filter(level=str(level)).order_by('?')[:2]
            else:
                questions = model_class.objects.filter(level=str(level), question_type=category_type).order_by('?')[:2]
            
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

        apply_choice_shuffle_to_items(request, level, all_questions)
        
        context = {
            'level': level,
            'question_type': question_type,
            'question_type_display': question_types.get(question_type, ''),
            'random_scope_description': random_scope_description(level),
            'num_questions': 10,
            'status': status,
            'questions': all_questions,
            'question_count_options': question_count_options,
        }
        return render(request, 'exams/question_list.html', context)
    
    elif question_type == 'mock_exam':
        unlock_status = _build_exam_unlock_status(request.user, str(level))
        if not unlock_status['mock_exam']['is_unlocked']:
            messages.warning(request, '模擬試験は、基本問題の各カテゴリで取り組み率80%以上になると解放されます。')
            return redirect('exams:exam_list')

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
            'listening_illustration_part1': 'リスニング第1部（会話応答）',
            'listening_illustration_part3': 'リスニング第3部（イラスト一致）',
            'listening_conversation': 'リスニング会話問題',
            'listening_passage': 'リスニング文章問題',
        }
        
        exam_structure = _get_mock_exam_structure(level)
        
        # 各カテゴリーから指定された数の問題を取得
        question_counter = 1
        regular_questions = []  # 通常の問題（大問1-3）
        reading_passages = []   # 長文読解問題（大問4）
        listening_questions = [] # リスニング問題（第1-3部）
        
        for category_type, model_class, num_questions in exam_structure:
            if model_class == ListeningQuestion:
                pool = list(model_class.objects.filter(level=str(level)).order_by('?'))
                if category_type == 'listening_illustration_part1':
                    pool = _filter_listening_illustrations(pool, part=1)
                    display_category = 'listening_illustration'
                elif category_type == 'listening_illustration_part3':
                    pool = _filter_listening_illustrations(pool, part=3)
                    display_category = 'listening_illustration_part3'
                else:
                    display_category = category_type
                questions = pool[:num_questions]
                for question in questions:
                    choices = ListeningChoice.objects.filter(question=question).order_by('order')
                    listening_questions.append({
                        'question': question,
                        'choices': choices,
                        'user_answer': None,
                        'is_correct': None,
                        'explanation': getattr(question, 'explanation', ''),
                        'category': display_category,
                        'category_name': category_names.get(category_type, category_type),
                        'question_type': 'listening_illustration',
                        'category_order': exam_structure.index((category_type, model_class, num_questions)),
                        'question_number': question_counter
                    })
                    question_counter += 1
            elif model_class == ReadingPassage:
                passages = model_class.objects.filter(level=str(level)).order_by('?')[:num_questions]
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
                questions = model_class.objects.filter(level=str(level), question_type=category_type).order_by('?')[:num_questions]
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
            listening_illustration = [
                q for q in listening_questions
                if q['category'] in ('listening_illustration', 'listening_illustration_part1')
            ]
            listening_illustration_part3 = [
                q for q in listening_questions if q['category'] == 'listening_illustration_part3'
            ]
            listening_conversation = [q for q in listening_questions if q['category'] == 'listening_conversation']
            listening_passage = [q for q in listening_questions if q['category'] == 'listening_passage']

            apply_choice_shuffle_to_items(request, level, all_questions)
            apply_choice_shuffle_to_items(request, level, listening_illustration)
            apply_choice_shuffle_to_items(request, level, listening_illustration_part3)
            apply_choice_shuffle_to_items(request, level, listening_conversation)
            apply_choice_shuffle_to_items(request, level, listening_passage)
            apply_choice_shuffle_to_passages(request, level, reading_passages)
            
            context = {
                'level': level,
                'question_type': question_type,
                'question_type_display': question_types.get(question_type, ''),
                'num_questions': len(all_questions) + sum(len(p['questions']) for p in reading_passages),
                'status': status,
                'questions': all_questions,
                'passages': reading_passages,
                'listening_illustration': listening_illustration,
                'listening_illustration_part3': listening_illustration_part3,
                'listening_conversation': listening_conversation,
                'listening_passage': listening_passage,
                'question_count_options': question_count_options,
            }
            return render(request, 'exams/mock_exam.html', context)
        else:
            apply_choice_shuffle_to_items(request, level, all_questions)
            listening_illustration_part3 = [
                q for q in listening_questions if q['category'] == 'listening_illustration_part3'
            ]
            context = {
                'level': level,
                'question_type': question_type,
                'question_type_display': question_types.get(question_type, ''),
                'num_questions': len(all_questions),
                'status': status,
                'questions': all_questions,
                'listening_illustration_part3': listening_illustration_part3,
                'question_count_options': question_count_options,
            }
            return render(request, 'exams/question_list.html', context)
    
    elif question_type in ('listening_illustration', 'listening_illustration_part3'):
        illustration_part = 1 if question_type == 'listening_illustration' and str(level) == '5' else (
            3 if question_type == 'listening_illustration_part3' else None
        )
        questions = ListeningQuestion.objects.filter(level=str(level)).order_by('id')
        if illustration_part is not None:
            questions = _filter_listening_illustrations(questions, part=illustration_part)
        logger.debug(f"Debug - Listening Illustration Questions: {len(questions)}")

        latest_answers = {
            answer.question_id: answer
            for answer in ListeningUserAnswer.objects.filter(
                user=request.user,
                question__in=questions
            ).select_related('question')
        }

        # 状態フィルターに応じて問題をフィルタリング
        questions = list(questions)
        if status == 'unanswered':
            questions = [q for q in questions if q.id not in latest_answers]
        elif status == 'correct':
            questions = [q for q in questions if q.id in latest_answers and latest_answers[q.id].is_correct]
        elif status == 'incorrect':
            questions = [q for q in questions if q.id in latest_answers and not latest_answers[q.id].is_correct]

        # 「全て」が選択された場合は制限しない
        if num_questions != 'all' and len(questions) > num_questions:
            questions = random.sample(questions, num_questions)
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

        apply_choice_shuffle_to_items(
            request,
            level,
            questions_with_choices,
            default_question_type='listening_illustration',
        )
        
        context = {
            'level': level,
            'question_type': question_type,
            'question_type_display': question_types.get(question_type, question_types.get('listening_illustration', '')),
            'num_questions': num_questions,
            'status': status,
            'questions': questions_with_choices,
            'question_count_options': question_count_options,
        }
        return render(request, 'exams/listening_illustration.html', context)
    
    elif question_type in ['listening_conversation', 'listening_passage']:
        # リスニング会話問題とリスニング文章問題の場合
        questions = Question.objects.filter(level=str(level), question_type=question_type).order_by('question_number')
        logger.debug(f"Debug - Regular Questions: {questions.count()}")  # デバッグ出力
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
        logger.debug(f"Debug - user_answer_dict keys: {list(user_answer_dict.keys())}")
        logger.debug(f"Debug - questions after filter: {[q.id for q in questions]}")
        logger.debug(f"Debug - status: {status}")
        
        # 問題数制限を適用
        if num_questions != 'all' and len(questions) > num_questions:
            questions = random.sample(questions, num_questions)
            questions.sort(key=lambda x: x.question_number)
        
        # POSTリクエストがある場合のみ回答処理を実行
        if request.method == 'POST':
            _snapshot_unlock_before_submit(request, request.user, level)
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
                        is_correct=is_correct,
                        answered_at=timezone.now()
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

        apply_choice_shuffle_to_items(
            request, level, questions_with_answers, default_question_type=question_type
        )
        
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
        passages = list(ReadingPassage.objects.filter(level=str(level)).order_by('id'))
        logger.debug(f"Debug - Reading Passages: {len(passages)}")  # デバッグ出力

        all_questions = ReadingQuestion.objects.filter(
            passage__in=passages
        ).select_related('passage').order_by('passage_id', 'question_number')

        questions_by_passage = {}
        for question in all_questions:
            questions_by_passage.setdefault(question.passage_id, []).append(question)

        latest_answers = _latest_reading_answers_by_question(request.user, level)

        # 状態フィルターを本文単位で適用
        filtered_passages = []
        for passage in passages:
            passage_questions = questions_by_passage.get(passage.id, [])
            if not passage_questions:
                continue

            answered_count = sum(1 for q in passage_questions if q.id in latest_answers)
            all_answered = answered_count == len(passage_questions)
            all_correct = all_answered and all(
                latest_answers[q.id].is_correct for q in passage_questions
            )

            include = True
            if status == 'unanswered':
                include = answered_count == 0
            elif status == 'correct':
                include = all_correct
            elif status == 'incorrect':
                include = answered_count > 0 and not all_correct

            if include:
                filtered_passages.append(passage)

        passages = filtered_passages

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
            questions_with_answers = []
            for question in questions_by_passage.get(passage.id, []):
                choices = ReadingChoice.objects.filter(question=question).order_by('order')
                correct_choice = choices.filter(is_correct=True).first()
                latest_answer = latest_answers.get(question.id)
                questions_with_answers.append({
                    'question': question,
                    'choices': choices,
                    'user_answer': latest_answer.selected_reading_choice if latest_answer else None,
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

    elif question_type == 'writing':
        questions = list(
            Question.objects.filter(
                level=str(level), question_type='writing'
            ).order_by('question_number')
        )
        wa_query = WritingUserAnswer.objects.filter(
            user=request.user,
            question__in=questions,
        ).order_by('-answered_at')
        wa_by_qid = {}
        for wa in wa_query:
            if wa.question_id not in wa_by_qid:
                wa_by_qid[wa.question_id] = wa

        if status == 'unanswered':
            questions = [q for q in questions if q.id not in wa_by_qid]
        elif status == 'correct':
            questions = [q for q in questions if q.id in wa_by_qid]
        elif status == 'incorrect':
            questions = []

        if num_questions != 'all' and len(questions) > num_questions:
            questions = random.sample(questions, num_questions)
            questions.sort(key=lambda x: x.question_number)

        questions_with_answers = []
        for question in questions:
            wa = wa_by_qid.get(question.id)
            questions_with_answers.append({
                'question': question,
                'choices': [],
                'user_answer': wa.response_text if wa else '',
                'is_correct': None,
                'correct_choice': None,
                'explanation': question.explanation,
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

    else:
        # 通常の問題の場合
        questions = Question.objects.filter(level=str(level), question_type=question_type).order_by('question_number')
        logger.debug(f"Debug - Regular Questions: {questions.count()}")  # デバッグ出力
        logger.debug(f"Debug - Level: {level}, Question Type: {question_type}")  # デバッグ出力
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
        logger.debug(f"Debug - user_answer_dict keys: {list(user_answer_dict.keys())}")
        logger.debug(f"Debug - questions after filter: {[q.id for q in questions]}")
        logger.debug(f"Debug - status: {status}")
        logger.debug(f"Debug - num_questions: {num_questions}")
        
        # 問題数制限を適用
        if num_questions != 'all' and len(questions) > num_questions:
            questions = random.sample(questions, num_questions)
            questions.sort(key=lambda x: x.question_number)
        
        logger.debug(f"Debug - Final questions count: {len(questions)}")
        logger.debug(f"Debug - Final question IDs: {[q.id for q in questions]}")
        
        # POSTリクエストがある場合のみ回答処理を実行
        if request.method == 'POST':
            _snapshot_unlock_before_submit(request, request.user, level)
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
                        is_correct=is_correct,
                        answered_at=timezone.now()
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

        apply_choice_shuffle_to_items(
            request, level, questions_with_answers, default_question_type=question_type
        )
        
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
    choices = list(question.choices.all().order_by('order', 'id'))
    choices = order_choices_for_display(
        request,
        question.level,
        question.question_type,
        question.id,
        choices,
    )
    
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
            is_correct=choice.is_correct,
            answered_at=timezone.now()
        )
        # 進捗を更新
        update_user_progress(request.user, question.level, question.question_type, choice.is_correct)
        messages.success(request, '回答を保存しました。')
    
    return redirect('exams:question_list', level=question.level)

@login_required
def submit_reading_comprehension(request, level):
    """長文読解問題の回答を提出"""
    if request.method == 'POST':
        _snapshot_unlock_before_submit(request, request.user, level)
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
                    is_correct=choice.is_correct,
                    answered_at=timezone.now()
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
        if question_type == 'writing' and str(level) != '3':
            messages.info(request, 'ライティング問題は英検3級のみです。')
            return redirect('exams:exam_list')
        if not _has_submittable_answers(request.POST):
            return _redirect_empty_submission(request, level, question_type)
        _snapshot_unlock_before_submit(request, request.user, level)
        status = request.POST.get('status', 'unanswered')
        # num_questionsが「全て」の場合は文字列、そうでなければ整数
        num_questions_param = request.POST.get('num_questions', 10)
        if num_questions_param == 'all':
            num_questions = 'all'
        else:
            num_questions = int(num_questions_param)
        
        logger.debug(f"Debug - Submit Answers: question_type={question_type}, level={level}, num_questions={num_questions}")
        logger.debug(f"Debug - POST data: {request.POST}")
        
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
                        # リスニング第1部は選択肢テキスト/番号の双方に対応して採点
                        is_correct = _is_correct_listening_illustration_answer(
                            question, selected_answer, request=request, level=level
                        )
                        ListeningUserAnswer.objects.create(
                            user=request.user,
                            question=question,
                            selected_answer=selected_answer,
                            is_correct=is_correct,
                            answered_at=timezone.now()
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
                                is_correct=choice.is_correct,
                                answered_at=timezone.now()
                            )
                            # 進捗を更新
                            update_user_progress(request.user, level, question.question_type, choice.is_correct)
                        except (Question.DoesNotExist, Choice.DoesNotExist):
                            continue
            
            # 今回回答したquestion_idをセッションに保存
            request.session[f'answered_questions_{question_type}_{level}'] = post_question_ids
            
            return redirect('exams:answer_results', level=level, question_type=question_type)
        
        elif question_type in ('listening_illustration', 'listening_illustration_part3'):
            illustration_part = 1 if question_type == 'listening_illustration' and str(level) == '5' else (
                3 if question_type == 'listening_illustration_part3' else None
            )
            questions = ListeningQuestion.objects.filter(level=str(level)).order_by('id')
            if illustration_part is not None:
                questions = _filter_listening_illustrations(questions, part=illustration_part)
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
                    # リスニング第1部は選択肢テキスト/番号の双方に対応して採点
                    is_correct = _is_correct_listening_illustration_answer(
                        question, selected_answer, request=request, level=level
                    )
                    ListeningUserAnswer.objects.create(
                        user=request.user,
                        question=question,
                        selected_answer=selected_answer,
                        is_correct=is_correct,
                        answered_at=timezone.now()
                    )
                    progress_type = question_type
                    if question_type == 'listening_illustration' and str(level) == '5':
                        progress_type = 'listening_illustration'
                    elif question_type == 'listening_illustration_part3':
                        progress_type = 'listening_illustration_part3'
                    update_user_progress(request.user, level, progress_type, is_correct)

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
                        is_correct=is_correct,
                        answered_at=timezone.now()
                    )
                    # 進捗を更新
                    update_user_progress(request.user, level, 'reading_comprehension', is_correct)

            # 今回回答したquestion_idと出題順序をセッションに保存
            request.session[f'answered_questions_{question_type}_{level}'] = post_question_ids
            
            return redirect('exams:answer_results', level=level, question_type=question_type)

        elif question_type == 'writing':
            questions = list(
                Question.objects.filter(
                    level=str(level), question_type='writing'
                ).order_by('question_number')
            )
            if num_questions != 'all' and len(questions) > num_questions:
                questions = random.sample(questions, num_questions)
                questions.sort(key=lambda x: x.question_number)

            post_question_ids = [
                int(key.replace('answer_', ''))
                for key in request.POST.keys()
                if key.startswith('answer_')
            ]

            WritingUserAnswer.objects.filter(
                user=request.user,
                question_id__in=post_question_ids,
            ).delete()

            for question_id in post_question_ids:
                text = (request.POST.get(f'answer_{question_id}', '') or '').strip()
                if not text:
                    continue
                question = Question.objects.get(id=question_id)
                rubric = get_writing_rubric(question)
                feedback = analyze_writing_response(text, rubric)
                WritingUserAnswer.objects.create(
                    user=request.user,
                    question_id=question_id,
                    response_text=text,
                    feedback_json=feedback,
                )
                update_user_progress(request.user, str(level), 'writing', True)

            request.session[f'answered_questions_{question_type}_{level}'] = post_question_ids

            return redirect('exams:answer_results', level=level, question_type=question_type)
        
        else:
            # 通常の問題の場合
            questions = Question.objects.filter(level=level, question_type=question_type).order_by('question_number')
            logger.debug(f"Debug - Regular Questions: {questions.count()}")  # デバッグ出力
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
            logger.debug(f"Debug - user_answer_dict keys: {list(user_answer_dict.keys())}")
            logger.debug(f"Debug - questions after filter: {[q.id for q in questions]}")
            logger.debug(f"Debug - status: {status}")
            
            # 問題数制限を適用
            if num_questions != 'all' and len(questions) > num_questions:
                questions = random.sample(questions, num_questions)
                questions.sort(key=lambda x: x.question_number)
            
            # POSTリクエストがある場合のみ回答処理を実行
            if request.method == 'POST':
                _snapshot_unlock_before_submit(request, request.user, level)
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
                            is_correct=is_correct,
                            answered_at=timezone.now()
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

            apply_choice_shuffle_to_items(
                request, level, questions_with_answers, default_question_type=question_type
            )
            
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
    if question_type == 'writing' and str(level) != '3':
        messages.info(request, 'ライティング問題は英検3級のみです。')
        return redirect('exams:exam_list')
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
                    'is_correct': _is_correct_listening_illustration_answer(
                        answer.question, answer.selected_answer,
                        request=request, level=level,
                    ),
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
                        'is_correct': _is_currently_correct_choice(answer.selected_choice),
                        'correct_choice': correct_choice,
                        'explanation': _format_objective_explanation(
                            answer.question.explanation, correct_choice
                        ),
                        'category': answer.question.question_type,
                        'order': answered_question_ids.index(question_id)
                    })
                except UserAnswer.DoesNotExist:
                    continue
        
        # 出題順序でソート
        answers_with_questions.sort(key=lambda x: x['order'])
        
        apply_choice_shuffle_to_items(
            request, level, answers_with_questions, create_if_missing=False
        )
        
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
        return _finalize_and_render_answer_results(request, context)
    
    elif question_type in ('listening_illustration', 'listening_illustration_part3'):
        # イラスト問題の場合
        # セッションから今回回答したquestion_idを取得
        session_key = f'answered_questions_{question_type}_{level}'
        answered_question_ids = request.session.get(session_key, [])
        
        logger.debug(f"Debug - Listening Illustration answered_question_ids: {answered_question_ids}")
        
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
            
            # 正解の選択肢を見つける（correct_answerはorder番号として保存されている）
            correct_choice = None
            if answer.question.correct_answer:
                try:
                    correct_order = int(answer.question.correct_answer)
                    correct_choice = choices.filter(order=correct_order).first()
                except (ValueError, TypeError):
                    # correct_answerが番号でない場合、テキストで検索
                    correct_choice = choices.filter(choice_text=answer.question.correct_answer).first()
            
            answers_with_questions.append({
                'question': answer.question,
                'choices': choices,
                'user_answer': answer.selected_answer,
                'is_correct': _is_correct_listening_illustration_answer(
                    answer.question, answer.selected_answer,
                    request=request, level=level,
                ),
                'correct_answer': answer.question.correct_answer,
                'correct_choice': correct_choice,  # 正解の選択肢オブジェクトを追加
                'explanation': getattr(answer.question, 'explanation', ''),
                'order': order_dict.get(answer.question.id, 0)  # 出題順序を追加
            })
        
        # 出題順序でソート
        answers_with_questions.sort(key=lambda x: x['order'])
        
        apply_choice_shuffle_to_items(
            request,
            level,
            answers_with_questions,
            default_question_type='listening_illustration',
            create_if_missing=False,
        )
        
        # 正解数を計算
        correct_count = sum(1 for answer in answers_with_questions if answer['is_correct'])
        total_count = len(user_answers)
        
        context = {
            'level': level,
            'question_type': question_type,
            'answers_with_questions': answers_with_questions,
            'correct_count': correct_count,
            'total_count': total_count,
        }
        return _finalize_and_render_answer_results(request, context)
    
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
                'is_correct': _is_currently_correct_choice(answer.selected_choice),
                'correct_choice': correct_choice,
                'explanation': _format_objective_explanation(
                    answer.question.explanation, correct_choice
                ),
                'order': order_dict.get(answer.question.id, 0)  # 出題順序を追加
            })
        
        # 出題順序でソート
        answers_with_questions.sort(key=lambda x: x['order'])
        
        apply_choice_shuffle_to_items(
            request,
            level,
            answers_with_questions,
            default_question_type=question_type,
            create_if_missing=False,
        )
        
        # 正解数を計算
        correct_count = sum(1 for answer in answers_with_questions if answer['is_correct'])
        total_count = len(user_answers)
        
        context = {
            'level': level,
            'question_type': question_type,
            'answers_with_questions': answers_with_questions,
            'correct_count': correct_count,
            'total_count': total_count,
        }
        return _finalize_and_render_answer_results(request, context)
    
    elif question_type == 'reading_comprehension':
        # 長文読解問題の場合
        # セッションから今回回答したquestion_idを取得
        session_key = f'answered_questions_{question_type}_{level}'
        answered_question_ids = request.session.get(session_key, [])
        
        # パッセージの順序を取得
        passage_order_key = f'passage_order_{question_type}_{level}'
        passage_order = request.session.get(passage_order_key, {})
        
        logger.debug(f"Debug - answered_question_ids: {answered_question_ids}")
        logger.debug(f"Debug - passage_order: {passage_order}")
        
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
                'is_correct': _is_currently_correct_choice(answer.selected_reading_choice),
                'correct_choice': correct_choice,
                'explanation': getattr(answer.reading_question, 'explanation', ''),
                'order': order_dict.get(answer.reading_question.id, 0)  # 出題順序を追加
            })
        
        logger.debug(f"Debug - passages_with_answers keys: {[p.id for p in passages_with_answers.keys()]}")
        
        # 各パッセージ内で出題順序でソート
        for passage in passages_with_answers:
            passages_with_answers[passage].sort(key=lambda x: x['order'])
        
        # パッセージを順序でソート
        sorted_passages = sorted(passages_with_answers.items(), key=lambda x: passage_order.get(str(x[0].id), 999))
        passages_with_answers = dict(sorted_passages)
        
        logger.debug(f"Debug - sorted passages: {[p.id for p in passages_with_answers.keys()]}")
        
        # 正解数を計算
        correct_count = sum(
            1
            for answers in passages_with_answers.values()
            for answer in answers
            if answer['is_correct']
        )
        total_count = len(user_answers)
        
        context = {
            'level': level,
            'question_type': question_type,
            'passages_with_answers': passages_with_answers,
            'correct_count': correct_count,
            'total_count': total_count,
        }
        return _finalize_and_render_answer_results(request, context)

    elif question_type == 'writing':
        session_key = f'answered_questions_{question_type}_{level}'
        answered_question_ids = request.session.get(session_key, [])
        order_dict = {
            qid: idx for idx, qid in enumerate(answered_question_ids)
        }
        user_answers = WritingUserAnswer.objects.filter(
            user=request.user,
            question_id__in=answered_question_ids,
        ).select_related('question')

        answers_with_questions = []
        for answer in user_answers:
            feedback_items = []
            if answer.feedback_json:
                feedback_items = answer.feedback_json.get('items', [])
            answers_with_questions.append({
                'question': answer.question,
                'choices': [],
                'user_answer': answer.response_text,
                'is_correct': None,
                'correct_choice': None,
                'explanation': answer.question.explanation,
                'feedback_items': feedback_items,
                'order': order_dict.get(answer.question.id, 0),
            })
        answers_with_questions.sort(key=lambda x: x['order'])

        submitted = sum(1 for a in user_answers if (a.response_text or '').strip())
        context = {
            'level': level,
            'question_type': question_type,
            'answers_with_questions': answers_with_questions,
            'correct_count': submitted,
            'total_count': len(user_answers),
        }
        return _finalize_and_render_answer_results(request, context)
    
    else:
        # 通常の問題の場合（会話問題など）
        # セッションから今回回答したquestion_idを取得
        session_key = f'answered_questions_{question_type}_{level}'
        answered_question_ids = request.session.get(session_key, [])
        
        # 今回回答したquestion_idのUserAnswerを取得（同一問題の複数回答がある場合は最新のみ採用）
        raw_user_answers = UserAnswer.objects.filter(
            user=request.user,
            question_id__in=answered_question_ids
        ).select_related('question', 'selected_choice').order_by('question_id', '-answered_at', '-id')
        latest_by_question_id = {}
        for user_answer in raw_user_answers:
            if user_answer.question_id not in latest_by_question_id:
                latest_by_question_id[user_answer.question_id] = user_answer
        user_answers = list(latest_by_question_id.values())
        
        # 出題順序に従ってソート
        # answered_question_idsの順序でソートする辞書を作成
        order_dict = {question_id: index for index, question_id in enumerate(answered_question_ids)}
        
        # 問題と回答を組み合わせる（出題順序でソート）
        answers_with_questions = []
        for answer in user_answers:
            choices = Choice.objects.filter(question=answer.question).order_by('order')
            correct_choice = choices.filter(is_correct=True).first()
            current_is_correct = bool(answer.selected_choice and answer.selected_choice.is_correct)
            
            # デバッグ: 正解が見つからない場合の警告
            if not correct_choice:
                logger.warning(f'問題{answer.question.id} (問題番号{answer.question.question_number}, タイプ{answer.question.question_type})で正解が見つかりませんでした')
                logger.warning(f'選択肢数: {choices.count()}, is_correct=Trueの数: {choices.filter(is_correct=True).count()}')
            
            answers_with_questions.append({
                'question': answer.question,
                'choices': choices,
                'user_answer': answer.selected_choice,
                'is_correct': current_is_correct,
                'correct_choice': correct_choice,
                'explanation': _format_objective_explanation(answer.question.explanation, correct_choice),
                'order': order_dict.get(answer.question.id, 0)  # 出題順序を追加
            })
        
        # 出題順序でソート
        answers_with_questions.sort(key=lambda x: x['order'])
    
        apply_choice_shuffle_to_items(
            request,
            level,
            answers_with_questions,
            default_question_type=question_type,
            create_if_missing=False,
        )

        # 正解数を計算
        correct_count = sum(1 for answer in answers_with_questions if answer['is_correct'])
        total_count = len(user_answers)
        
        context = {
            'level': level,
            'question_type': question_type,
            'answers_with_questions': answers_with_questions,
            'correct_count': correct_count,
            'total_count': total_count,
        }
        return _finalize_and_render_answer_results(request, context)

@login_required
def progress_view(request):
    """学習進捗を表示"""
    user = request.user
    level_order = ['5', '4', '3', '2', '1', 'pre1']
    available_levels = list(
        Question.objects.values_list('level', flat=True).distinct()
    )
    ordered = [lv for lv in level_order if lv in available_levels]
    leftover = [lv for lv in available_levels if lv not in level_order]
    levels = ordered + sorted(leftover)

    level_labels = {
        '4': '英検4級',
        '3': '英検3級',
        '2': '英検2級',
        '1': '英検1級',
        'pre1': '英検準1級',
    }
    level_entries = [
        (lv, level_labels.get(lv, f'英検{lv}級')) for lv in levels
    ]

    # 各級の進捗を取得
    progress_data = {}
    for level in levels:
        level_progress = UserProgress.objects.filter(user=user, level=level)
        progress_data[level] = {
            'grammar_fill': progress_to_dict(level_progress.filter(question_type='grammar_fill').first(), level, 'grammar_fill', user),
            'conversation_fill': progress_to_dict(level_progress.filter(question_type='conversation_fill').first(), level, 'conversation_fill', user),
            'word_order': progress_to_dict(level_progress.filter(question_type='word_order').first(), level, 'word_order', user),
            'reading_comprehension': progress_to_dict(level_progress.filter(question_type='reading_comprehension').first(), level, 'reading_comprehension', user),
            'writing': progress_to_dict(level_progress.filter(question_type='writing').first(), level, 'writing', user),
            'listening_illustration': progress_to_dict(level_progress.filter(question_type='listening_illustration').first(), level, 'listening_illustration', user),
            'listening_conversation': progress_to_dict(level_progress.filter(question_type='listening_conversation').first(), level, 'listening_conversation', user),
            'listening_passage': progress_to_dict(level_progress.filter(question_type='listening_passage').first(), level, 'listening_passage', user),
        }
        
        # デバッグ出力を追加
        logger.debug(f"Debug - Progress data for level {level}:")
        for question_type, progress in progress_data[level].items():
            logger.debug(f"  {question_type}: last_attempted={progress['last_attempted']}")
    
    return render(request, 'exams/progress.html', {
        'progress_data': progress_data,
        'levels': levels,
        'level_entries': level_entries,
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
    logger.debug(f"Debug - Updating progress for user={user.username}, level={level}, type={question_type}, is_correct={is_correct}")
    logger.debug(f"Debug - Before update: last_attempted={progress.last_attempted}")
    progress.update_progress(is_correct)
    logger.debug(f"Debug - After update: last_attempted={progress.last_attempted}")


def _latest_reading_answers_by_question(user, level):
    """長文読解の各設問に対する最新回答を返す。"""
    latest_answers = {}
    if user is None or level is None:
        return latest_answers

    answers = ReadingUserAnswer.objects.filter(
        user=user,
        reading_question__passage__level=str(level),
    ).select_related('selected_reading_choice').order_by(
        'reading_question_id', '-answered_at', '-id'
    )
    for answer in answers:
        if answer.reading_question_id not in latest_answers:
            latest_answers[answer.reading_question_id] = answer
    return latest_answers


def _reading_passage_progress_counts(user, level):
    """長文読解の進捗を本文単位（完了本文数/総本文数）で返す。"""
    if level is None:
        return 0, 0

    question_rows = list(
        ReadingQuestion.objects.filter(
            passage__level=str(level)
        ).values('id', 'passage_id')
    )
    if not question_rows:
        return 0, 0

    total_by_passage = {}
    question_to_passage = {}
    for row in question_rows:
        passage_id = row['passage_id']
        question_id = row['id']
        total_by_passage[passage_id] = total_by_passage.get(passage_id, 0) + 1
        question_to_passage[question_id] = passage_id

    latest_answers = _latest_reading_answers_by_question(user, level)
    answered_counts_by_passage = {}
    for question_id in latest_answers.keys():
        passage_id = question_to_passage.get(question_id)
        if passage_id is None:
            continue
        answered_counts_by_passage[passage_id] = answered_counts_by_passage.get(passage_id, 0) + 1

    completed_passages = 0
    for passage_id, total_count in total_by_passage.items():
        if answered_counts_by_passage.get(passage_id, 0) == total_count:
            completed_passages += 1

    return completed_passages, len(total_by_passage)


def _total_questions_for_type(level, question_type):
    """レベル・問題タイプごとのマスタ上の総問題数。"""
    if not level or not question_type:
        return 0
    if question_type == 'listening_illustration':
        qs = ListeningQuestion.objects.filter(level=str(level))
        if str(level) == '5':
            return len(_filter_listening_illustrations(qs, part=1))
        return qs.count()
    if question_type == 'listening_illustration_part3':
        qs = ListeningQuestion.objects.filter(level=str(level))
        return len(_filter_listening_illustrations(qs, part=3))
    if question_type == 'reading_comprehension':
        _, total_passages = _reading_passage_progress_counts(None, level)
        return total_passages
    return Question.objects.filter(level=level, question_type=question_type).count()


def _progress_rate_for_type(user, level, question_type):
    """指定タイプの取り組み率（0-100）を返す。"""
    total_questions = _total_questions_for_type(level, question_type)
    if total_questions <= 0:
        return 0
    answered_distinct = _distinct_answered_question_count(user, level, question_type)
    return min(100, round((answered_distinct / total_questions) * 100, 1))


def _build_exam_unlock_status(user, level):
    """ランダム問題・模擬試験の解放状態を返す。"""
    category_progress = []
    for question_type in _foundation_question_types_for_level(level):
        total_questions = _total_questions_for_type(level, question_type)
        if total_questions <= 0:
            continue
        progress_rate = _progress_rate_for_type(user, level, question_type)
        category_progress.append({
            'question_type': question_type,
            'display_name': QUESTION_TYPE_LABELS.get(question_type, question_type),
            'progress_rate': progress_rate,
            'total_questions': total_questions,
        })

    random_ready_count = sum(
        1 for item in category_progress
        if item['progress_rate'] >= RANDOM_UNLOCK_MIN_RATE
    )
    random_unlocked = random_ready_count >= RANDOM_UNLOCK_REQUIRED_CATEGORIES

    mock_unlocked = bool(category_progress) and all(
        item['progress_rate'] >= MOCK_EXAM_UNLOCK_MIN_RATE
        for item in category_progress
    )
    mock_remaining = [
        {
            **item,
            'remaining_rate': round(
                MOCK_EXAM_UNLOCK_MIN_RATE - item['progress_rate'], 1
            ),
        }
        for item in category_progress
        if item['progress_rate'] < MOCK_EXAM_UNLOCK_MIN_RATE
    ]

    return {
        'random': {
            'is_unlocked': random_unlocked,
            'ready_count': random_ready_count,
            'required_count': RANDOM_UNLOCK_REQUIRED_CATEGORIES,
            'required_rate': RANDOM_UNLOCK_MIN_RATE,
        },
        'mock_exam': {
            'is_unlocked': mock_unlocked,
            'required_rate': MOCK_EXAM_UNLOCK_MIN_RATE,
            'remaining_categories': mock_remaining,
            'total_categories': len(category_progress),
        },
        'foundation_progress': category_progress,
    }


def _snapshot_unlock_before_submit(request, user, level):
    """Store unlock flags before batch submit updates progress rates."""
    store_pre_submit_unlock_snapshot(
        request,
        _build_exam_unlock_status(user, str(level)),
        str(level),
    )


def _finalize_and_render_answer_results(request, context):
    """Attach session achievement messages and render answer results."""
    level = str(context['level'])
    unlock_status = _build_exam_unlock_status(request.user, context['level'])
    pre_unlock = pop_pre_submit_unlock_snapshot(request, level)
    gamification_result = process_gamification_after_session(
        request.user,
        question_type=context['question_type'],
    )
    daily_goal = get_daily_mission_goal(request, level=level)
    context['achievement_messages'] = build_session_achievements(
        user=request.user,
        level=level,
        question_type=context['question_type'],
        correct_count=context.get('correct_count', 0),
        total_count=context.get('total_count', 0),
        unlock_status=unlock_status,
        pre_unlock=pre_unlock,
        session_count=context.get('total_count', 0),
        daily_goal=daily_goal,
        streak_incremented=gamification_result['streak_incremented'],
        streak_count=gamification_result['streak_count'],
    )
    context['new_badges'] = gamification_result['new_badges']
    return render(request, 'exams/answer_results.html', context)


def _distinct_answered_question_count(user, level, question_type):
    """そのレベル・タイプで進捗率の分子となる件数。"""
    if user is None or level is None or question_type is None:
        return 0
    if question_type == 'listening_illustration':
        answers = ListeningUserAnswer.objects.filter(
            user=user,
            question__level=str(level),
        )
        if str(level) == '5':
            part1_ids = {
                question.id
                for question in _filter_listening_illustrations(
                    ListeningQuestion.objects.filter(level=str(level)), part=1
                )
            }
            return answers.filter(question_id__in=part1_ids).count()
        return answers.count()
    if question_type == 'listening_illustration_part3':
        part3_ids = {
            question.id
            for question in _filter_listening_illustrations(
                ListeningQuestion.objects.filter(level=str(level)), part=3
            )
        }
        return ListeningUserAnswer.objects.filter(
            user=user,
            question_id__in=part3_ids,
        ).count()
    if question_type == 'reading_comprehension':
        completed_passages, _ = _reading_passage_progress_counts(user, level)
        return completed_passages
    if question_type == 'writing':
        return WritingUserAnswer.objects.filter(
            user=user,
            question__level=str(level),
            question__question_type='writing',
        ).values('question_id').distinct().count()
    return UserAnswer.objects.filter(
        user=user,
        question__level=level,
        question__question_type=question_type,
    ).values('question_id').distinct().count()


def progress_to_dict(progress, level=None, question_type=None, user=None):
    """進捗オブジェクトを辞書に変換。取り組み率は「全問に一度は答えた」割合（ユニーク問題数/総問題数、上限100%）。"""
    if progress is None:
        logger.debug(f"Debug - progress_to_dict: progress is None")
        # 過去7日間のデータを取得（progressがNoneでも）
        daily_data = {}
        from django.utils import timezone
        from datetime import datetime, time, timedelta
        
        for i in range(7):
            date = timezone.localdate() - timedelta(days=i)
            date_start = timezone.make_aware(datetime.combine(date, time.min))
            date_end = timezone.make_aware(datetime.combine(date, time.max))
            date_str = date.isoformat()
            
            if question_type == 'listening_illustration':
                from questions.models import ListeningUserAnswer
                daily_count = ListeningUserAnswer.objects.filter(
                    user=user,  # userパラメータが必要
                    question__level=str(level),
                    answered_at__range=(date_start, date_end)
                ).count()
            elif question_type == 'reading_comprehension':
                from .models import ReadingUserAnswer
                daily_count = ReadingUserAnswer.objects.filter(
                    user=user,  # userパラメータが必要
                    reading_question__passage__level=str(level),
                    answered_at__range=(date_start, date_end)
                ).count()
            elif question_type == 'writing':
                daily_count = WritingUserAnswer.objects.filter(
                    user=user,
                    question__level=str(level),
                    question__question_type='writing',
                    answered_at__range=(date_start, date_end),
                ).count()
            else:
                daily_count = UserAnswer.objects.filter(
                    user=user,  # userパラメータが必要
                    question__level=level,
                    question__question_type=question_type,
                    answered_at__range=(date_start, date_end)
                ).count()
            
            daily_data[date_str] = daily_count
        
        total_questions = _total_questions_for_type(level, question_type)
        answered_distinct = _distinct_answered_question_count(user, level, question_type)
        progress_rate = 0
        if total_questions > 0:
            progress_rate = min(
                100,
                round((answered_distinct / total_questions) * 100, 1),
            )
        
        return {
            'accuracy_rate': 0,
            'total_attempts': 0,
            'correct_answers': 0,
            'incorrect_answers': 0,
            'progress_rate': progress_rate,
            'answered_questions': answered_distinct,
            'total_questions': total_questions,
            'today_attempts': 0,
            'daily_data': daily_data,
            'last_attempted': None
        }
    
    # 不正解数を計算
    incorrect_answers = progress.total_attempts - progress.correct_answers
    
    total_questions = _total_questions_for_type(level, question_type)
    answered_distinct = _distinct_answered_question_count(
        progress.user, level, question_type
    )
    # 取り組み率: ユニークな問題に一度以上答えた割合（100% = 全問に一度は回答済み）
    progress_rate = 0
    if total_questions > 0:
        progress_rate = min(
            100,
            round((answered_distinct / total_questions) * 100, 1),
        )
    
    # 今日の取り組み数を取得（暦日は TIME_ZONE、既定は Asia/Tokyo）
    from django.utils import timezone
    from datetime import datetime, time, timedelta
    today = timezone.localdate()
    today_start = timezone.make_aware(datetime.combine(today, time.min))
    today_end = timezone.make_aware(datetime.combine(today, time.max))
    
    if question_type == 'listening_illustration':
        from questions.models import ListeningUserAnswer
        today_attempts = ListeningUserAnswer.objects.filter(
            user=progress.user,
            question__level=str(level),
            answered_at__range=(today_start, today_end)
        ).count()
    elif question_type == 'reading_comprehension':
        from .models import ReadingUserAnswer
        today_attempts = ReadingUserAnswer.objects.filter(
            user=progress.user,
            reading_question__passage__level=str(level),
            answered_at__range=(today_start, today_end)
        ).count()
    elif question_type == 'writing':
        today_attempts = WritingUserAnswer.objects.filter(
            user=progress.user,
            question__level=str(level),
            question__question_type='writing',
            answered_at__range=(today_start, today_end),
        ).count()
    else:
        today_attempts = UserAnswer.objects.filter(
            user=progress.user,
            question__level=level,
            question__question_type=question_type,
            answered_at__range=(today_start, today_end)
        ).count()
    
    # 過去7日間の取り組み数を取得
    daily_data = {}
    for i in range(7):
        date = timezone.localdate() - timedelta(days=i)
        date_start = timezone.make_aware(datetime.combine(date, time.min))
        date_end = timezone.make_aware(datetime.combine(date, time.max))
        date_str = date.isoformat()
        
        if question_type == 'listening_illustration':
            from questions.models import ListeningUserAnswer
            daily_count = ListeningUserAnswer.objects.filter(
                user=progress.user,
                question__level=str(level),
                answered_at__range=(date_start, date_end)
            ).count()
        elif question_type == 'reading_comprehension':
            from .models import ReadingUserAnswer
            daily_count = ReadingUserAnswer.objects.filter(
                user=progress.user,
                reading_question__passage__level=str(level),
                answered_at__range=(date_start, date_end)
            ).count()
        elif question_type == 'writing':
            daily_count = WritingUserAnswer.objects.filter(
                user=progress.user,
                question__level=str(level),
                question__question_type='writing',
                answered_at__range=(date_start, date_end),
            ).count()
        else:
            daily_count = UserAnswer.objects.filter(
                user=progress.user,
                question__level=level,
                question__question_type=question_type,
                answered_at__range=(date_start, date_end)
            ).count()
        
        daily_data[date_str] = daily_count
    
    result = {
        'accuracy_rate': progress.accuracy_rate,
        'total_attempts': progress.total_attempts,
        'correct_answers': progress.correct_answers,
        'incorrect_answers': incorrect_answers,
        'progress_rate': progress_rate,
        'answered_questions': answered_distinct,
        'total_questions': total_questions,
        'today_attempts': today_attempts,
        'daily_data': daily_data,  # 過去7日間のデータを追加
        'last_attempted': progress.last_attempted.astimezone(timezone.get_current_timezone()).strftime('%Y年%m月%d日 %H:%M') if progress.last_attempted else None,  # 日付をJSTで日本語形式の文字列に変換
    }
    logger.debug(f"Debug - progress_to_dict: result.last_attempted={result['last_attempted']}")
    return result

def _allowed_progress_levels():
    level_order = ['5', '4', '3', '2', '1', 'pre1']
    available_levels = list(
        Question.objects.values_list('level', flat=True).distinct()
    )
    ordered = [lv for lv in level_order if lv in available_levels]
    leftover = [lv for lv in available_levels if lv not in level_order]
    return ordered + sorted(leftover)


def _clear_user_progress_for_level(user, level):
    """指定級の学習進捗と回答履歴を削除する。"""
    level_str = str(level)
    UserProgress.objects.filter(user=user, level=level_str).delete()
    UserAnswer.objects.filter(user=user, question__level=level_str).delete()
    WritingUserAnswer.objects.filter(user=user, question__level=level_str).delete()
    ReadingUserAnswer.objects.filter(
        user=user,
        reading_question__passage__level=level_str,
    ).delete()
    ListeningUserAnswer.objects.filter(
        user=user,
        question__level=level_str,
    ).delete()


@login_required
def clear_progress(request):
    """表示中の級の学習進捗をクリア"""
    if request.method == 'POST':
        level = request.POST.get('level', '').strip()
        allowed_levels = _allowed_progress_levels()
        level_labels = {
            '4': '英検4級',
            '3': '英検3級',
            '2': '英検2級',
            '1': '英検1級',
            'pre1': '英検準1級',
        }
        if level not in allowed_levels:
            messages.error(request, 'クリア対象の級が不正です。')
            return redirect('exams:progress')
        _clear_user_progress_for_level(request.user, level)
        label = level_labels.get(level, f'英検{level}級')
        messages.success(request, f'{label}の学習進捗をクリアしました。')
    return redirect('exams:progress')

@login_required
@ratelimit(key='user', rate='5/h', method='POST', block=False)
@ratelimit(key='ip', rate='10/h', method='POST', block=False)
def feedback_form(request):
    """フィードバックフォームを表示・処理"""
    from .forms import FeedbackForm

    if request.method == 'POST':
        ip_address = get_client_ip(request)
        if getattr(request, 'limited', False):
            logger.warning(
                f'フィードバック送信レート制限超過: username={request.user.username}, '
                f'ip={ip_address}, user_agent={request.META.get("HTTP_USER_AGENT", "Unknown")}'
            )
            messages.error(
                request,
                '送信回数が上限に達しました。しばらく時間をおいてから再度お試しください。',
            )
            form = FeedbackForm(request.POST)
            return render(request, 'exams/feedback_form.html', {'form': form})

        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            logger.info(
                f'フィードバック送信: username={request.user.username}, ip={ip_address}, '
                f'type={feedback.feedback_type}, title={feedback.title[:80]!r}, '
                f'user_agent={request.META.get("HTTP_USER_AGENT", "Unknown")}'
            )
            return redirect('exams:feedback_success')

        if form.errors.get('website'):
            logger.warning(
                f'フィードバック送信拒否（ハニーポット）: username={request.user.username}, '
                f'ip={ip_address}, user_agent={request.META.get("HTTP_USER_AGENT", "Unknown")}'
            )
    else:
        form = FeedbackForm()

    return render(request, 'exams/feedback_form.html', {'form': form})

@login_required
def feedback_success(request):
    """フィードバック送信成功ページ"""
    return render(request, 'exams/feedback_success.html')

@csrf_exempt
def sitemap_xml(request):
    """公開ページのみを含む動的サイトマップ"""
    base_url = "https://eiken-app.fly.dev"
    today = datetime.now().strftime('%Y-%m-%d')

    urls = [
        {
            'loc': f"{base_url}/",
            'lastmod': today,
            'changefreq': 'weekly',
            'priority': '1.0',
        },
        {
            'loc': f"{base_url}/privacy-policy/",
            'lastmod': today,
            'changefreq': 'monthly',
            'priority': '0.5',
        },
    ]

    response = HttpResponse(
        render_to_string('exams/sitemap.xml', {'urls': urls}),
        content_type='application/xml',
    )
    return response
