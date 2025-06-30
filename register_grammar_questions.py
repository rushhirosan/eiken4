#!/usr/bin/env python
"""
文法語彙問題をデータベースに登録するスクリプト
"""

import os
import sys
import django

# Djangoの設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eiken_project.settings')
django.setup()

from questions.models import GrammarFillQuestion, Choice
import re

def parse_grammar_questions(file_path):
    """文法語彙問題のテキストファイルを解析して問題データを抽出"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 問題を分割
    questions = content.split('---\n')
    parsed_questions = []
    
    for question_text in questions:
        if not question_text.strip():
            continue
            
        # 問題番号を抽出
        question_match = re.search(r'問題(\d+):\s*(.+)', question_text)
        if not question_match:
            continue
            
        question_number = int(question_match.group(1))
        question_content = question_match.group(2).strip()
        
        # 選択肢を抽出
        choices_match = re.search(r'選択肢\d+:\s*((?:\d+\.\s*[^\n]+\n?)+)', question_text)
        if not choices_match:
            continue
            
        choices_text = choices_match.group(1)
        choices = []
        for line in choices_text.strip().split('\n'):
            choice_match = re.search(r'(\d+)\.\s*(.+)', line)
            if choice_match:
                choice_number = int(choice_match.group(1))
                choice_text = choice_match.group(2).strip()
                choices.append((choice_number, choice_text))
        
        # 正解を抽出
        correct_match = re.search(r'【正解\d+】\s*(\d+)\.\s*(.+)', question_text)
        if not correct_match:
            continue
            
        correct_number = int(correct_match.group(1))
        correct_text = correct_match.group(2).strip()
        
        # 解説を抽出
        explanation_match = re.search(r'【解説\d+】\s*(.+)', question_text, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else ""
        
        parsed_questions.append({
            'question_number': question_number,
            'question_text': question_content,
            'choices': choices,
            'correct_number': correct_number,
            'correct_text': correct_text,
            'explanation': explanation
        })
    
    return parsed_questions

def register_grammar_questions():
    """文法語彙問題をデータベースに登録"""
    file_path = 'questions/grammar_fill_questions.txt'
    
    if not os.path.exists(file_path):
        print(f"エラー: ファイル {file_path} が見つかりません。")
        return
    
    print("文法語彙問題の解析を開始...")
    questions = parse_grammar_questions(file_path)
    print(f"解析完了: {len(questions)}問の問題を発見")
    
    # 既存の問題を削除（オプション）
    existing_count = GrammarFillQuestion.objects.filter(level='4').count()
    print(f"既存の問題数: {existing_count}")
    
    # 新しい問題を登録
    registered_count = 0
    for question_data in questions:
        try:
            # 問題を作成
            question = GrammarFillQuestion.objects.create(
                question_text=question_data['question_text'],
                level='4',
                explanation=question_data['explanation']
            )
            
            # 選択肢を作成
            for choice_number, choice_text in question_data['choices']:
                is_correct = (choice_number == question_data['correct_number'])
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=is_correct
                )
            
            registered_count += 1
            print(f"問題{question_data['question_number']}を登録しました")
            
        except Exception as e:
            print(f"問題{question_data['question_number']}の登録でエラー: {e}")
    
    print(f"\n登録完了: {registered_count}問の問題を登録しました")
    print(f"データベース内の総問題数: {GrammarFillQuestion.objects.filter(level='4').count()}")

if __name__ == '__main__':
    register_grammar_questions() 