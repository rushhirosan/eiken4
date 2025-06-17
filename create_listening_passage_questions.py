import os
import django
import re
import sys

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eiken_project.settings')
django.setup()

from exams.models import Question, Choice

def extract_questions_from_file(file_path):
    questions_data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 問題ブロックを分割
        question_blocks = content.split('---')
        for block in question_blocks:
            if not block.strip():
                continue
            # 問題番号を抽出
            number_match = re.search(r'No\.(\d+):', block)
            if not number_match:
                continue
            question_number = int(number_match.group(1))
            # パッセージ文を抽出（No.X: から Question No.X: の直前まで）
            passage_match = re.search(r'No\.\d+:\s*(.*?)\n\s*Question No\.', block, re.DOTALL)
            passage = passage_match.group(1).strip() if passage_match else ''
            # 問題文を抽出
            question_text_match = re.search(r'Question No\.\d+:\s*(.*?)\n\s*1\.', block, re.DOTALL)
            question_text = question_text_match.group(1).strip() if question_text_match else ''
            # 選択肢を抽出
            choices = []
            for i in range(1, 5):
                choice_match = re.search(rf'{i}\.\s*(.*?)(?=\n\d\.\s|\n【正解|\n$)', block, re.DOTALL)
                if choice_match:
                    choices.append(choice_match.group(1).strip())
            # 正解を抽出
            correct_match = re.search(r'【正解\d+】\s*(\d+)\.', block)
            correct_choice_index = int(correct_match.group(1)) - 1 if correct_match else 0
            # 解説を抽出
            explanation_match = re.search(r'【解説\d+】\s*(.+)', block, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else ''
            # データ追加
            if question_text and choices:
                questions_data.append({
                    'question_number': question_number,
                    'passage': passage,
                    'question_text': question_text,
                    'choices': choices,
                    'correct_choice_index': correct_choice_index,
                    'explanation': explanation
                })
    return questions_data

# ファイルから問題を読み取る
file_path = 'questions/listening_passage_questions.txt'
questions_data = extract_questions_from_file(file_path)

# 問題を作成
for q_data in questions_data:
    # passageもquestion_textの先頭に付与（必要なら）
    question = Question.objects.create(
        question_type='listening_passage',
        level=4,  # 英検4級
        question_number=q_data['question_number'],
        question_text=q_data['passage'] + '\n' + q_data['question_text'],
        explanation=q_data['explanation']
    )
    for i, choice_text in enumerate(q_data['choices']):
        Choice.objects.create(
            question=question,
            choice_text=choice_text,
            is_correct=(i == q_data['correct_choice_index']),
            order=i + 1
        )
print(f"Created {len(questions_data)} listening passage questions") 