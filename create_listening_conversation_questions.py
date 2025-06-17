import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eiken_project.settings')
django.setup()

from exams.models import Question, Choice

def parse_questions_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 問題ブロックを分割
    question_blocks = content.split('---')
    
    questions_data = []
    for block in question_blocks:
        if not block.strip():
            continue
            
        # 会話文を抽出
        conversation_match = re.search(r'No\.\d+:\n(.*?)\n\nQuestion', block, re.DOTALL)
        conversation = conversation_match.group(1).strip() if conversation_match else ''
        
        # 問題文を抽出
        question_match = re.search(r'Question No\.\d+:\s*(.*?)\n', block)
        question_text = question_match.group(1).strip() if question_match else ''
        
        # 選択肢を抽出
        choices = []
        # 【正解】の前までの部分を取得
        choices_section = block.split('【正解】')[0]
        # 問題文の後ろから選択肢を抽出（空行の数に依存しない）
        after_question = False
        for line in choices_section.split('\n'):
            if after_question and re.match(r'^\d+\.', line.strip()):
                choice_text = re.sub(r'^\d+\.\s*', '', line.strip())
                if choice_text and not choice_text.startswith('【'):
                    choices.append(choice_text)
                if len(choices) == 4:
                    break
            if line.strip() == question_text:
                after_question = True
        
        # 正解を抽出
        correct_match = re.search(r'【正解\d+】\s*(\d+)\.', block)
        correct_answer_number = int(correct_match.group(1)) if correct_match else 0
        
        # 解説を抽出
        explanation_match = re.search(r'【解説\d+】\s*(.*?)(?=\n---|$)', block, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else ''
        
        if question_text and len(choices) == 4:
            questions_data.append({
                'conversation': conversation,
                'question_text': question_text,
                'choices': choices,
                'correct_answer_number': correct_answer_number,
                'explanation': explanation
            })
    
    return questions_data

def create_listening_conversation_questions():
    # 既存の問題を削除
    Question.objects.filter(question_type='listening_conversation').delete()
    
    # テキストファイルから問題を読み込む
    questions_data = parse_questions_from_file('questions/listening_conversation_questions.txt')
    
    for i, data in enumerate(questions_data, 1):
        # 問題を作成
        question = Question.objects.create(
            level='4',
            question_type='listening_conversation',
            question_text=data['question_text'],
            listening_text=data['conversation'],  # 会話文を保存
            explanation=data['explanation'],
            audio_file=f'/static/audio/part2/listening_conversation_question{i}.mp3',
            question_number=i
        )
        
        # 選択肢を作成
        for j, choice_text in enumerate(data['choices'], 1):
            Choice.objects.create(
                question=question,
                choice_text=choice_text,
                is_correct=(j == data['correct_answer_number']),
                order=j
            )

if __name__ == '__main__':
    create_listening_conversation_questions()
    print("リスニング第二部会話問題を作成しました。") 