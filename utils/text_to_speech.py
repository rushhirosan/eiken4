#!/usr/bin/env python3
import os
from gtts import gTTS
import re

def create_listening_illustration_audio_31_to_40():
    """
    リスニングイラスト問題31-40の音声ファイルを作成
    会話文、質問文、選択肢すべてを含む
    """
    
    # 問題データ（会話文、質問、選択肢、正解）
    questions = {
        31: {
            'conversation': "That watch is pretty. Yes, but it's expensive. You're right.",
            'question': "Question No.31:",
            'choices': [
                "1. Let's go to another store.",
                "2. It's in a box.",
                "3. At the mall."
            ]
        },
        32: {
            'conversation': "You look happy. I am. I got a new job at the library. That's great.",
            'question': "Question No.32:",
            'choices': [
                "1. I'm so excited.",
                "2. Sure you can.",
                "3. I have that book."
            ]
        },
        33: {
            'conversation': "I love this cake. Do you want some more? Just a little.",
            'question': "Question No.33:",
            'choices': [
                "1. For a few minutes.",
                "2. I'm not a good cook.",
                "3. Here you are."
            ]
        },
        34: {
            'conversation': "Where did you go on vacation? I went to Spain. Did you eat seafood?",
            'question': "Question No.34:",
            'choices': [
                "1. Yes. It was delicious.",
                "2. I'm studying Spanish.",
                "3. Well, I have a meeting."
            ]
        },
        35: {
            'conversation': "Where did you go last weekend? I went snowboarding at Mt. Baker. How was it?",
            'question': "Question No.35:",
            'choices': [
                "1. We went by car.",
                "2. There were five.",
                "3. It was exciting."
            ]
        },
        36: {
            'conversation': "I'd like an apple pie for dessert. I'll make some. Great. How many apples do you need?",
            'question': "Question No.36:",
            'choices': [
                "1. It was so delicious.",
                "2. Let's get four or five.",
                "3. No, I'm full."
            ]
        },
        37: {
            'conversation': "Is your math test today? Yes, it is. Good luck!",
            'question': "Question No.37:",
            'choices': [
                "1. I'll do my best.",
                "2. It was difficult.",
                "3. You'll like it."
            ]
        },
        38: {
            'conversation': "Where did you take this photo? In Toronto. Who are the people with you?",
            'question': "Question No.38:",
            'choices': [
                "1. During the vacation.",
                "2. It was cold and rainy.",
                "3. My aunt and uncle."
            ]
        },
        39: {
            'conversation': "Were you at Sam's birthday party? Yes. How was it?",
            'question': "Question No.39:",
            'choices': [
                "1. I had a good time.",
                "2. That's a good idea.",
                "3. I don't have a ticket."
            ]
        },
        40: {
            'conversation': "Do you have any plans for summer vacation? Yes. I'll go to Hawaii. What will you do there?",
            'question': "Question No.40:",
            'choices': [
                "1. On the beach.",
                "2. It will be hot.",
                "3. I'll visit my cousins."
            ]
        }
    }
    
    # 出力ディレクトリを作成
    output_dir = "static/audio/part1"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"ディレクトリを作成しました: {output_dir}")
    
    # 各問題の音声ファイルを作成
    for question_num in range(31, 41):
        print(f"問題{question_num}の音声ファイルを作成中...")
        
        # テキストを組み立て
        question_data = questions[question_num]
        
        # 会話文（男性と女性の声で交互に）
        conversation = question_data['conversation']
        # 質問文
        question = question_data['question']
        # 選択肢
        choices = question_data['choices']
        
        # 完全なテキストを作成
        full_text = f"{conversation} {question} {' '.join(choices)}"
        
        # 音声ファイルを作成
        output_file = os.path.join(output_dir, f"listening_illustration_question{question_num}.mp3")
        
        try:
            tts = gTTS(text=full_text, lang='en', slow=False)
            tts.save(output_file)
            print(f"音声ファイルを作成しました: {output_file}")
        except Exception as e:
            print(f"問題{question_num}の音声ファイル作成中にエラーが発生しました: {str(e)}")
    
    print("音声ファイル作成完了！")

if __name__ == "__main__":
    create_listening_illustration_audio_31_to_40() 