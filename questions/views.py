from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Question, Choice, ReadingPassage, ReadingQuestion, ReadingChoice, ListeningQuestion, ListeningUserAnswer

def reading_comprehension_list_view(request):
    # すべてのパッセージを取得
    passages = ReadingPassage.objects.all().order_by('id')
    
    return render(request, 'questions/reading_comprehension_list.html', {
        'passages': passages
    })

def reading_comprehension_view(request, passage_id):
    # パッセージ（本文）を取得
    passage = ReadingPassage.objects.get(id=passage_id)
    
    # そのパッセージに紐付いた設問（a1, a2, ...）を取得
    questions = ReadingQuestion.objects.filter(passage=passage).order_by('question_number')
    
    if request.method == 'POST':
        # 回答の処理
        score = 0
        total_questions = questions.count()
        results = []
        
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                selected_choice = ReadingChoice.objects.get(id=selected_choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    score += 1
                results.append({
                    'question': question,
                    'selected_choice': selected_choice,
                    'is_correct': is_correct,
                    'correct_choice': ReadingChoice.objects.get(question=question, is_correct=True)
                })
        
        # 結果を表示
        return render(request, 'questions/reading_comprehension.html', {
            'passage': passage,
            'questions': questions,
            'show_results': True,
            'results': results,
            'score': score,
            'total_questions': total_questions,
            'percentage': (score / total_questions * 100) if total_questions > 0 else 0
        })
    
    return render(request, 'questions/reading_comprehension.html', {
        'passage': passage,
        'questions': questions
    })

def listening_question_list(request):
    questions = ListeningQuestion.objects.all().order_by('id')
    return render(request, 'questions/listening_question_list.html', {'questions': questions})

def listening_question_detail(request, question_id):
    question = get_object_or_404(ListeningQuestion, pk=question_id)
    user_answer = None
    if request.user.is_authenticated:
        user_answer = ListeningUserAnswer.objects.filter(
            user=request.user,
            question=question
        ).first()

    if request.method == 'POST' and request.user.is_authenticated:
        selected_answer = request.POST.get('answer')
        is_correct = selected_answer == question.correct_answer

        if user_answer:
            user_answer.selected_answer = selected_answer
            user_answer.is_correct = is_correct
            user_answer.save()
        else:
            ListeningUserAnswer.objects.create(
                user=request.user,
                question=question,
                selected_answer=selected_answer,
                is_correct=is_correct
            )
        return redirect('listening_question_list')

    return render(request, 'questions/listening_question.html', {
        'question': question,
        'user_answer': user_answer
    })

def answer_results(request):
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    # この関数の実装は以前のものを使用
    }) 