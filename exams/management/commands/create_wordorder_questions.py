from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

class Command(BaseCommand):
    help = 'Creates word order questions from a text file'

    def handle(self, *args, **options):
        file_path = 'wordorder_questions.txt'
        self.stdout.write(f'語句整序問題の登録を開始します...\nファイルパス: {file_path}')

        try:
            # 既存の語句整序問題を削除
            Question.objects.filter(question_type='word_order').delete()
            self.stdout.write('既存の語句整序問題を削除しました')

            # ファイルから問題を解析して登録
            questions = parse_questions_from_file(file_path)
            total_questions = register_questions(questions)
            
            self.stdout.write(f'合計 {total_questions} 問を追加しました')
            self.stdout.write('語句整序問題の登録が完了しました')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'エラーが発生しました: {str(e)}'))

def parse_questions_from_file(file_path):
    questions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        print(f"ファイルを読み込みました。内容の長さ: {len(content)} 文字")
        
        # 問題ブロックを抽出（2行以上の空行で分割）
        blocks = re.split(r'\n\n+', content)
        print(f"問題ブロック数: {len(blocks)}")
        
        # すべての問題ブロックを処理
        for block in blocks:
            if not block.strip():  # 空のブロックをスキップ
                continue
                
            try:
                print(f"\n処理中の問題ブロック:\n{block}")
                
                # 問題番号と日本語の問題文を抽出
                question_match = re.search(r'\((\d+)\)\s+(.+)', block)
                if not question_match:
                    print("問題番号が見つかりません")
                    continue
                    
                question_number = int(question_match.group(1))
                japanese_text = question_match.group(2)
                print(f"問題番号: {question_number}")
                print(f"日本語の問題文: {japanese_text}")
                
                # 選択肢を抽出
                choices_match = re.search(r'①\s*([^②]+)②\s*([^③]+)③\s*([^④]+)④\s*([^⑤]+)⑤\s*([^\n]+)', block)
                if not choices_match:
                    print("選択肢が見つかりません")
                    continue
                
                choices = [
                    choices_match.group(1).strip(),
                    choices_match.group(2).strip(),
                    choices_match.group(3).strip(),
                    choices_match.group(4).strip(),
                    choices_match.group(5).strip()
                ]
                print(f"選択肢: {choices}")
                
                # 英文を抽出（( ) [2番目] ( ) [4番目] ( ) the math test. の形式）
                english_match = re.search(r'\(\s*\)\s*\[2番目\]\s*\(\s*\)\s*\[4番目\]\s*\(\s*\)\s*(.+?)(?=\n)', block)
                if english_match:
                    english_text = english_match.group(0).strip()  # 全体のパターンを取得
                else:
                    english_text = ""
                print(f"英文: {english_text}")
                
                # 正解と選択肢を抽出
                answer_match = re.search(r'→\s*【正解】(\d+)\s*([①②③④⑤])\s*─\s*([①②③④⑤])', block)
                if not answer_match:
                    print("正解が見つかりません")
                    continue
                    
                correct_answer = int(answer_match.group(1))
                correct_choice1 = answer_match.group(2)
                correct_choice2 = answer_match.group(3)
                
                # 選択肢の組み合わせを抽出
                choices_pattern = r'(\d+)\s*([①②③④⑤])\s*─\s*([①②③④⑤])'
                answer_choices = []
                for match in re.finditer(choices_pattern, block):
                    if match.group(0).startswith('→'):
                        continue
                    answer_choices.append(match.group(0))
                    if len(answer_choices) == 4:  # 4つの選択肢のみを取得
                        break
                
                print(f"回答の選択肢: {answer_choices}")
                print(f"正解: {correct_answer}")
                
                # 解説を抽出
                explanation_match = re.search(r'【解説】(.+?)(?=\n\n|\Z)', block, re.DOTALL)
                if explanation_match:
                    explanation = explanation_match.group(1).strip()
                else:
                    explanation = ""
                print(f"解説: {explanation}")
                
                questions.append({
                    'number': question_number,
                    'japanese_text': japanese_text,
                    'choices': choices,
                    'english_text': english_text,
                    'correct_answer': correct_answer,
                    'answer_choices': answer_choices,
                    'explanation': explanation
                })
                print(f"問題 {question_number} を解析しました")
                
            except Exception as e:
                print(f"問題の解析中にエラーが発生しました: {str(e)}")
                continue
    
    return questions

def register_questions(questions):
    total_questions = 0
    for question_data in questions:
        try:
            # 問題文のフォーマットを修正
            question_text = f"({question_data['number']}) {question_data['japanese_text']}<br>"
            # 選択肢を1行にまとめる
            choices_text = " ".join([f"{i} {choice}" for i, choice in zip(['①', '②', '③', '④', '⑤'], question_data['choices'])])
            question_text += f"{choices_text}<br>"
            # 英文を選択肢の後に表示
            question_text += f"{question_data['english_text']}"

            # 解説はQuestionモデルのexplanationフィールドにのみ保存
            explanation = question_data['explanation']

            question = Question.objects.create(
                level=4,
                question_type='word_order',
                question_text=question_text,
                explanation=explanation
            )

            # 選択肢を登録（選択肢の組み合わせを表示しない）
            for i, choice_text in enumerate(question_data['answer_choices'], 1):
                # 選択肢の組み合わせ部分を削除
                choice_text = re.sub(r'\d+\s*([①②③④⑤])\s*─\s*([①②③④⑤])', r'\1 ─ \2', choice_text)
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(i == question_data['correct_answer']),
                    order=i
                )

            total_questions += 1
            print(f"問題 {total_questions} を追加しました")

        except Exception as e:
            print(f"問題の登録中にエラーが発生しました: {str(e)}")
            continue

    return total_questions