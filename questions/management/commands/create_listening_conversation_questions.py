from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re
import os

def parse_questions_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 問題ブロックを分割
    question_blocks = content.split('---')
    
    questions_data = []
    for block in question_blocks:
        if not block.strip():
            continue
        
        # 問題番号を抽出
        number_match = re.search(r'No\.(\d+):', block)
        question_number = int(number_match.group(1)) if number_match else None
        
        # 会話文を抽出
        conversation_match = re.search(r'No\.\d+:\n(.*?)\n\nQuestion', block, re.DOTALL)
        conversation = conversation_match.group(1).strip() if conversation_match else ''
        
        # 問題文を抽出
        question_match = re.search(r'Question No\.\d+:\s*(.*?)\n', block)
        question_text = question_match.group(1).strip() if question_match else ''
        
        # 選択肢を抽出
        choices = []
        choices_section = block.split('【正解】')[0]
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
        
        if question_text and len(choices) == 4 and question_number is not None:
            questions_data.append({
                'question_number': question_number,
                'conversation': conversation,
                'question_text': question_text,
                'choices': choices,
                'correct_answer_number': correct_answer_number,
                'explanation': explanation
            })
    
    return questions_data

class Command(BaseCommand):
    help = 'listening_conversation_questions.txt から問題11-20の会話問題を登録する'

    def handle(self, *args, **options):
        # 既存の問題を削除（11-20のみ）
        Question.objects.filter(
            question_type='listening_conversation',
            question_number__in=range(11, 21)
        ).delete()
        print('既存のリスニング会話問題（11-20）を削除しました')
        
        # テキストファイルから問題を読み込む
        questions_data = parse_questions_from_file('questions/listening_conversation_questions.txt')
        print(f'parse_questions_from_fileで抽出された問題数: {len(questions_data)}')
        for idx, data in enumerate(questions_data, 1):
            print(f'--- 問題{idx} ---')
            print(f'question_number: {data.get("question_number")!r}')
            print(f'question_text: {data.get("question_text")!r}')
            print(f'choices: {data.get("choices")!r}')
            print(f'correct_answer_number: {data.get("correct_answer_number")!r}')
            print(f'conversation: {data.get("conversation")!r}')
            print(f'explanation: {data.get("explanation")!r}')
        
        for data in questions_data:
            question_number = data['question_number']
            # 11-20のみを処理
            if question_number < 11 or question_number > 20:
                continue
            # 問題を作成
            question = Question.objects.create(
                level='4',
                question_type='listening_conversation',
                question_text=data['question_text'],
                listening_text=data['conversation'],  # 会話文を保存
                explanation=data['explanation'],
                audio_file=f'/static/audio/part2/listening_conversation_question{question_number}.mp3',
                question_number=question_number
            )
            # 選択肢を作成
            for j, choice_text in enumerate(data['choices'], 1):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(j == data['correct_answer_number']),
                    order=j
                )
            print(f'問題{question_number}を登録')
        print('問題11-20のリスニング会話問題を登録しました')

def extract_conversation_and_question(text):
    """会話と問題を抽出"""
    lines = text.strip().split('\n')
    conversation = []
    question = []
    is_question = False
    skip_until_next_question = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # No.X: をスキップ
        if re.match(r'No\.\d+:', line):
            skip_until_next_question = False
            continue
            
        # 正解と解説が始まったら、次の問題までスキップ
        if line.startswith('【正解') or line.startswith('【解説'):
            skip_until_next_question = True
            continue
            
        if skip_until_next_question:
            continue
            
        # Question No.X: の場合
        if line.startswith('Question No.'):
            is_question = True
            # Question のみを追加
            question.append("Question")
            continue
            
        # 選択肢をスキップ
        if re.match(r'^\d+\.', line):
            continue
            
        # M: と W: を除去
        if line.startswith('M:') or line.startswith('W:'):
            line = line[2:].strip()
            
        if is_question:
            question.append(line)
        else:
            conversation.append(line)
    
    return '\n'.join(conversation), '\n'.join(question)

def combine_audio_files(conversation_audio, question_audio, output_path):
    """音声ファイルを結合"""
    # 音声ファイルを読み込み
    conversation = AudioSegment.from_mp3(conversation_audio)
    question = AudioSegment.from_mp3(question_audio)
    
    # 1秒の無音を作成
    silence = AudioSegment.silent(duration=1000)
    
    # 音声を結合（会話 → 1秒の無音 → Question → 1秒の無音 → 問題文）
    combined = conversation + silence + question
    
    # 結合した音声を保存
    combined.export(output_path, format="mp3")
    
    # 一時ファイルを削除
    os.remove(conversation_audio)
    os.remove(question_audio)

async def text_to_speech(text, output_path, voice):
    """テキストを音声ファイルに変換する"""
    try:
        # 出力ディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 音声を生成
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        print(f"音声ファイルを {output_path} に保存しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

async def main():
    # 入力ファイルのパス
    input_file = 'questions/listening_illustration_questions.txt'
    
    # 出力ディレクトリ
    output_dir = 'static/audio/part1'
    os.makedirs(output_dir, exist_ok=True)
    
    # ファイルを読み込み
    with open(input_file, 'r', encoding='utf-8') as f:
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
        
        # 11問目から20問目のみを処理
        if question_number < 11 or question_number > 20:
            continue
        
        # 会話と問題を抽出
        conversation, question = extract_conversation_and_question(block)
        
        # 音声ファイルのパス（11から始まる番号に調整）
        adjusted_number = question_number - 10  # 11→1, 12→2, ...
        conversation_audio = os.path.join(output_dir, f'temp_conversation_{adjusted_number}.mp3')
        question_audio = os.path.join(output_dir, f'temp_question_{adjusted_number}.mp3')
        output_audio = os.path.join(output_dir, f'listening_illustration_question{adjusted_number}.mp3')
        
        # 会話の音声を生成（男性の声）
        await text_to_speech(conversation, conversation_audio, "en-US-GuyNeural")
        
        # 問題の音声を生成（女性の声）
        await text_to_speech(question, question_audio, "en-US-JennyNeural")
            
        # 音声ファイルを結合
        combine_audio_files(conversation_audio, question_audio, output_audio)
                
        print(f"Processed question {question_number} (saved as {adjusted_number})")

 