import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eiken_project.settings')
django.setup()

from exams.models import Question, Choice

def parse_questions_from_file(file_path):
    questions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # 問題ブロックを抽出（2行以上の空行で分割）
        blocks = re.split(r'\n\n+', content)
        print(f"Found {len(blocks)} blocks")
        
        for block in blocks:
            if not block.strip():  # 空のブロックをスキップ
                continue
                
            try:
                print(f"\nProcessing block:\n{block}")
                
                # 問題番号を取得
                number_match = re.search(r'\((\d+)\)', block)
                if not number_match:
                    print("No question number found")
                    continue
                    
                question_number = int(number_match.group(1))
                print(f"Found question number: {question_number}")
                
                # 問題文と解答部分を分離
                parts = block.split('→')
                if len(parts) < 2:
                    print(f"Question {question_number}: No answer section found")
                    continue
                
                question_part = parts[0].strip()
                answer_part = parts[1].strip()
                print(f"Question part:\n{question_part}")
                print(f"Answer part:\n{answer_part}")
                
                # 選択肢を抽出
                choices = []
                # 選択肢行を見つける（数字で始まる行）
                lines = question_part.split('\n')
                for line in lines:
                    if re.match(r'^\d+\s+', line.strip()):
                        print(f"Found choice line: {line}")
                        # 選択肢を個別に抽出
                        choice_line = line.strip()
                        # 選択肢を抽出（各選択肢を個別に取得）
                        for i in range(1, 5):
                            pattern = fr'{i}\s+([^.?]+[.?])'
                            match = re.search(pattern, choice_line)
                            if match:
                                choice_text = match.group(1).strip()
                                if choice_text.endswith('.') or choice_text.endswith('?'):
                                    choice_text = choice_text[:-1]
                                choices.append(choice_text)
                        print(f"Extracted choices: {choices}")
                        break
                
                # 正解を抽出（番号を取得）
                correct_match = re.search(r'【正解】\s*(\d+)\s+([^【]+)', answer_part)
                if not correct_match:
                    print(f"Question {question_number}: No correct answer found")
                    continue
                correct_answer_number = int(correct_match.group(1))
                print(f"Found correct answer number: {correct_answer_number}")
                
                # 解説を抽出
                explanation_match = re.search(r'【解説】(.+?)(?=\(\d+\)|$)', answer_part, re.DOTALL)
                explanation = explanation_match.group(1).strip() if explanation_match else ""
                print(f"Found explanation: {explanation[:50]}...")
                
                # 問題文から選択肢行を除いた部分を取得
                question_lines = []
                for line in lines:
                    if not re.match(r'^\d+\s+', line.strip()):
                        question_lines.append(line.strip())
                clean_question = '\n'.join(question_lines).strip()
                print(f"Clean question text:\n{clean_question}")
                
                if len(choices) == 4:
                    questions.append({
                        'question_number': question_number,
                        'question_text': clean_question,
                        'choices': choices,
                        'correct_answer_number': correct_answer_number,
                        'explanation': explanation
                    })
                    print(f"Successfully added question {question_number}")
                else:
                    print(f"Question {question_number}: Found {len(choices)} choices instead of 4: {choices}")
            
            except Exception as e:
                print(f"Error processing block: {str(e)}")
                continue
        
        print(f"\nTotal questions extracted: {len(questions)}")
        for q in questions:
            print(f"Question {q['question_number']}: {q['choices']}")
    
    return questions

def register_questions():
    # 既存の会話問題を削除
    Question.objects.filter(question_type='conversation_fill').delete()
    print("既存の会話問題を削除しました")
    
    # 新しい問題を追加
    questions = parse_questions_from_file('conversation_learnings.txt')
    
    success_count = 0
    for q_data in questions:
        try:
            # Create question
            question = Question.objects.create(
                question_text=q_data['question_text'],
                question_type='conversation_fill',
                explanation=q_data['explanation'],
                level=4  # 4級として設定
            )
            
            # Create choices
            for i, choice_text in enumerate(q_data['choices'], 1):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(i == q_data['correct_answer_number'])
                )
            
            success_count += 1
            print(f"Added question {q_data['question_number']}: {q_data['question_text'][:50]}...")
        except Exception as e:
            print(f"エラー: 問題 {q_data['question_number']} の追加に失敗しました - {str(e)}")
    
    print(f"\n登録完了: {success_count}問をデータベースに追加しました")

if __name__ == '__main__':
    register_questions() 