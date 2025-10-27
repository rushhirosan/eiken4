# 英検問題更新フロー統合仕様書

## 概要
英検4級の全問題タイプの更新・管理フローを統合的に定義します。過去問PDFから問題を取得するフローから、データベースへの登録まで、すべての工程を網羅しています。

## プロジェクト構造とディレクトリ役割

### プロジェクト全体の構造

```
プロジェクトホーム/
├── accounts/          # ユーザー認証（Djangoアプリ）
├── exams/             # 試験機能（Djangoアプリ）
├── questions/         # 問題データ管理（Djangoアプリ）
├── eiken_project/     # Djangoプロジェクト設定
├── config/            # デプロイ設定（Dockerfile, fly.toml等）
├── data/              # データファイル
│   ├── questions/     # 問題データ（テキストファイル）
│   └── *.json         # エクスポートデータ
├── docs/              # ドキュメント
├── scripts/           # スクリプト
├── static/            # 静的ファイル
│   ├── audio/         # 音声ファイル
│   └── images/        # 画像ファイル
├── templates/         # テンプレート
├── utils/             # ユーティリティ
├── venv/              # Python仮想環境
├── manage.py          # Django管理コマンド
└── .github/           # GitHub設定
```

### ディレクトリ構成と役割

#### exams/（試験・テスト機能）
**役割**: ウェブサイトの試験機能を提供するDjangoアプリ
- **対象**: ユーザー（学習者）
- **機能**: 問題表示・回答受付・結果表示・進捗管理
- **URL**: `/exams/level/4/`, `/exams/question/1/`
- **テンプレート**: `exams/question_list.html`, `exams/answer_results.html`
- **主要ファイル**:
  - `views.py` - 問題表示・回答処理（1595行）
  - `models.py` - 進捗・回答履歴・フィードバック
  - `templates/exams/` - 試験用HTMLテンプレート
  - `management/commands/update_audio_paths.py` - 音声パス更新

#### questions/（問題データ管理）
**役割**: 問題データの登録・更新・管理を行うDjangoアプリ
- **対象**: 管理者（開発者）
- **機能**: 問題データの登録・更新・管理コマンド
- **URL**: `/questions/reading/`, `/questions/listening/`
- **テンプレート**: `questions/reading_comprehension_list.html`
- **主要ファイル**:
  - `models.py` - 問題データの詳細モデル（107行）
  - `views.py` - 問題データの表示（141行）
  - `management/commands/` - 問題登録・更新コマンド（8個）

#### データフロー
```
1. questions/で問題データを登録・更新（管理コマンド）
   ↓
2. exams/で問題を表示・回答受付（ウェブサイト）
   ↓
3. exams/で回答結果・進捗を管理（ユーザー体験）
```

#### 依存関係
- **exams/がquestions/のモデルを使用**
- **exams/の`Question`は共通モデル**
- **questions/の詳細モデルは専用機能**

#### 管理コマンドの役割分担

**exams/management/commands/（試験機能関連）**
- `update_audio_paths.py` - 音声ファイルパス更新（音声ファイル管理）

**questions/management/commands/（問題データ管理）**
- `register_grammar_fill_questions.py` - 文法・語彙問題登録
- `register_conversation_fill_questions.py` - 会話補充問題登録
- `register_wordorder_fill_questions.py` - 語順選択問題登録
- `register_reading_comprehension_questions.py` - 長文読解問題登録
- `register_listening_illustration_questions.py` - リスニング第1部登録
- `create_listening_conversation_questions.py` - リスニング第2部作成
- `create_listening_passage_questions.py` - リスニング第3部作成

**命名規則の注意**
- `exams/` = 試験・テスト機能（ウェブサイトの試験ページ）
- `questions/` = 問題データ管理（問題の登録・更新）
- 名前と役割が完全に一致していないが、既存コードの安定性を優先

#### その他のディレクトリ

**accounts/（ユーザー認証）**
- 役割: ユーザー認証機能
- 機能: サインアップ・ログイン

**config/（デプロイ設定）**
- 役割: 本番環境のデプロイ設定
- ファイル: Dockerfile, fly.toml, Procfile, requirements.txt, runtime.txt
- サイズ: 本番環境での動作に必須

**data/（データファイル）**
- 役割: 問題データの管理
- `questions/` - テキストファイル（7個）
- `*.json` - エクスポートデータ
- 整理: 重複ファイルを削除済み（3個削除）

**docs/（ドキュメント）**
- 役割: プロジェクトドキュメント
- ファイル: README.md, todo.md, question_update_flow_specification.md

**scripts/（スクリプト）**
- 役割: 起動スクリプト
- ファイル: start.sh

**static/（静的ファイル）**
- 役割: ウェブサイトの静的リソース
- `audio/` - 音声ファイル（40個のリスニング問題）
- `images/` - 画像ファイル（リスニングイラスト40個）

**templates/（テンプレート）**
- 役割: 共通テンプレート
- ファイル: base.html, privacy_policy.html

**utils/（ユーティリティ）**
- 役割: 問題取得・音声生成ツール
- ファイル: pdf_text_extractor.py, pdf_image_extractor.py, text_to_speech.py, text_to_speech_conversation.py
- 整理: 重複スクリプトを統合済み（2個統合）

## 全体フロー概要

### 1. 過去問PDF取得フロー
1. **過去問PDFダウンロード**: [英検公式サイト](https://www.eiken.or.jp/eiken/exam/grade_4/)から過去問PDFを取得
2. **PDF解析**: `utils/pdf_text_extractor.py`でテキスト抽出
3. **画像抽出**: `utils/pdf_image_extractor.py`でリスニング問題の画像を`static/images/part1/`に抽出
4. **問題分類**: 各カテゴリごとに問題を分類・整理
5. **テキストファイル保存**: 各問題タイプのテキストファイルに保存
6. **音声生成**: `utils/text_to_speech*.py`でリスニング問題の音声を`static/audio/part*/`に生成
7. **ファイルパス更新**: `python manage.py update_audio_paths`でデータベースのファイルパスを更新
8. **データベース登録**: 管理コマンドでデータベースに登録

### 2. データベース更新フロー
1. **バックアップ作成**: 既存データのバックアップ
2. **テキストファイル編集**: 問題データの編集・追加
3. **更新実行**: 管理コマンドでデータベース更新
4. **検証**: フロントエンドでの動作確認

## 問題タイプ一覧

### 1. 文法・語彙問題 (Grammar Fill Questions)
- **ファイル**: `questions/grammar_fill_questions.txt`
- **モデル**: `GrammarFillQuestion`, `GrammarFillChoice`
- **コマンド**: `register_grammar_fill_questions`
- **特徴**: 最もシンプルな形式、完全更新

### 2. 会話補充問題 (Conversation Fill Questions)
- **ファイル**: `questions/conversation_questions.txt`
- **モデル**: `Question` (question_type='conversation_fill')
- **コマンド**: `register_conversation_fill_questions`
- **特徴**: 会話の文脈を理解する問題

### 3. 語順選択問題 (Word Order Questions)
- **ファイル**: `questions/wordorder_questions.txt`
- **モデル**: `Question` (question_type='word_order')
- **コマンド**: `register_wordorder_fill_questions`
- **特徴**: 語順の理解を問う問題

### 4. 長文読解問題 (Reading Comprehension Questions)
- **ファイル**: `questions/reading_comprehesion_questions.txt`
- **モデル**: `ReadingPassage`, `ReadingQuestion`, `ReadingChoice`
- **コマンド**: `register_reading_comprehension_questions`
- **特徴**: 1つのパッセージに複数問題が関連

### 5. リスニング問題

#### 5.1 リスニング第1部: イラスト問題 (Listening Illustration Questions)
- **ファイル**: `questions/listening_illustration_questions.txt`
- **モデル**: `ListeningQuestion`, `ListeningChoice`
- **コマンド**: `register_listening_illustration_questions`
- **特徴**: 音声ファイル（MP3）+ 画像ファイル（PNG）

#### 5.2 リスニング第2部: 会話問題 (Listening Conversation Questions)
- **ファイル**: `questions/listening_conversation_questions.txt`
- **モデル**: `Question` (question_type='listening_conversation')
- **コマンド**: `create_listening_conversation_questions`
- **特徴**: 音声ファイル連携

#### 5.3 リスニング第3部: 文章問題 (Listening Passage Questions)
- **ファイル**: `questions/listening_passage_questions.txt`
- **モデル**: `Question` (question_type='listening_passage')
- **コマンド**: `create_listening_passage_questions`
- **特徴**: 音声ファイル連携

## データモデル

### 共通モデル (exams/models.py)

#### Question
```python
class Question(models.Model):
    LEVELS = [
        ('4', 'Grade 4'),
        ('3', 'Grade 3'),
        ('2', 'Grade 2'),
        ('1', 'Grade 1'),
        ('pre1', 'Pre-Grade 1'),
    ]
    QUESTION_TYPES = [
        ('grammar_fill', '文法・語彙問題'),
        ('conversation_fill', '会話補充問題'),
        ('word_order', '語順選択問題'),
        ('reading_comprehension', '長文読解問題'),
        ('listening_conversation', 'リスニング第2部: 会話問題'),
        ('listening_illustration', 'リスニング第1部: イラスト問題'),
        ('listening_passage', 'リスニング第3部: 文章問題'),
    ]
    
    level = models.CharField(max_length=10, choices=LEVELS)
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    question_text = models.TextField()
    listening_text = models.TextField(blank=True, null=True)
    explanation = models.TextField(blank=True, default='')
    audio_file = models.CharField(max_length=255, blank=True)
    image_file = models.CharField(max_length=255, blank=True)
    question_number = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Choice
```python
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField()
```

### 専用モデル (questions/models.py)

#### GrammarFillQuestion
```python
class GrammarFillQuestion(models.Model):
    question_text = models.TextField()
    level = models.CharField(max_length=10, choices=LEVELS, default='4')
    question_number = models.IntegerField()
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### GrammarFillChoice
```python
class GrammarFillChoice(models.Model):
    question = models.ForeignKey(GrammarFillQuestion, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField()
```

#### ListeningQuestion
```python
class ListeningQuestion(models.Model):
    question_text = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    audio = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=200)
    level = models.CharField(max_length=10, choices=LEVELS, default='4')
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### ReadingPassage
```python
class ReadingPassage(models.Model):
    text = models.TextField()
    level = models.CharField(max_length=10, choices=LEVELS, default='4')
    identifier = models.CharField(max_length=1, default='a')
    created_at = models.DateTimeField(auto_now_add=True)
```

## 過去問PDF取得フロー詳細

### 1. 過去問PDF取得
- **ソース**: [英検公式サイト 4級過去問](https://www.eiken.or.jp/eiken/exam/grade_4/)
- **ファイル形式**: PDF（問題冊子・スクリプト）
- **取得頻度**: 年3回（1次試験実施後）

### 2. PDF解析・抽出

#### 2.1 テキスト抽出
```bash
# PDFからテキストを抽出
python utils/pdf_text_extractor.py
```

**機能:**
- PDFファイルからテキストを抽出
- ページ範囲指定可能
- UTF-8でテキストファイルに保存

**設定例:**
```python
pdf_path = "/path/to/eiken/2025-1-1ji-4kyu_script.pdf"
output_path = "output.txt"
page_range = (13, 15)  # 特定ページ範囲
```

#### 2.2 画像抽出（リスニング第1部用）
```bash
# PDFから画像を抽出
python utils/pdf_image_extractor.py
```

**機能:**
- リスニング第1部のイラスト画像を抽出
- 自動的に色反転処理（黒背景問題の解決）
- PNG形式で保存

**設定例:**
```python
pdf_path = "/path/to/eiken/2025-1-1ji-4kyu.pdf"
output_dir = "static/images/part1/"
start_number = 1
```

### 3. 音声・画像ファイル生成・配置

#### 3.1 リスニング第1部（イラスト問題）
```bash
# リスニング第1部の音声を生成
python utils/text_to_speech.py
```

**機能:**
- 会話文、質問文、選択肢の音声を生成
- gTTS（Google Text-to-Speech）を使用
- MP3形式で保存

**出力先:**
- `static/audio/part1/listening_illustration_question{番号}.mp3`

#### 3.2 リスニング第2部（会話問題）
```bash
# リスニング第2部の音声を生成
python utils/text_to_speech_conversation.py
```

**機能:**
- 会話文と質問文を分離して音声生成
- Edge TTSを使用
- 話者別音声生成（M: 男性、W: 女性）
- 音声ファイルの結合

**出力先:**
- `static/audio/part2/listening_conversation_question{番号}.mp3`

#### 3.3 リスニング第3部（文章問題）
```bash
# リスニング第3部の音声を生成
python utils/text_to_speech_conversation.py
```

**出力先:**
- `static/audio/part3/listening_passage_question{番号}.mp3`

#### 3.4 画像ファイル抽出
```bash
# PDFから画像を抽出
python utils/pdf_image_extractor.py
```

**機能:**
- リスニング第1部のイラスト画像を抽出
- 自動的に色反転処理（黒背景問題の解決）
- PNG形式で保存

**出力先:**
- `static/images/part1/listening_illustration_image{番号}.png`

### 4. 問題分類・整理

#### 4.1 手動分類プロセス
1. **PDF解析結果の確認**: 抽出されたテキストの確認
2. **問題タイプ別分類**: 各問題を適切なカテゴリに分類
3. **テキストファイル編集**: 各問題タイプのテキストファイルに整理
4. **形式統一**: 統一された形式で問題を記録

#### 4.2 分類基準
- **文法・語彙問題**: 空欄補充形式
- **会話補充問題**: 会話文の空欄補充
- **語順選択問題**: 語順を選択する形式
- **長文読解問題**: 長文に基づく複数問題
- **リスニング問題**: 音声を聞いて答える問題

## 更新フロー共通仕様

### 1. データソース形式
- **文字エンコーディング**: UTF-8
- **区切り文字**: `---` で問題を分割
- **問題番号**: 連番で管理

### 2. 共通更新手順

#### 2.1 事前準備
```bash
# 1. バックアップ作成
python manage.py dumpdata questions > data/questions_backup.json

# 2. テキストファイル編集
# questions/[問題タイプ]_questions.txt を編集
```

#### 2.2 更新実行
```bash
# 各問題タイプに対応するコマンドを実行
python manage.py register_[問題タイプ]_questions
```

#### 2.3 検証
```bash
# 1. 登録件数確認
python manage.py shell
>>> from [models] import [QuestionModel]
>>> [QuestionModel].objects.count()

# 2. フロントエンド確認
# http://localhost:5001 で問題表示確認
```

### 3. エラーハンドリング

#### 3.1 共通エラー
- **文字エンコーディングエラー**: UTF-8で保存確認
- **正規表現エラー**: 問題形式の確認
- **データベースエラー**: 権限・接続確認

#### 3.2 ログ出力形式
```python
# 成功時
self.stdout.write(self.style.SUCCESS(f'問題{question_number}を登録しました'))

# エラー時
self.stdout.write(self.style.ERROR(f'問題{question_number}の登録でエラー: {str(e)}'))
```

## 問題タイプ別詳細仕様

### 文法・語彙問題（詳細）

#### データ形式
```
問題1:
A : Did you () the speech contest, Mika? 
B : Yes, I did. I'm happy. 

選択肢1:
1. walk
2. fall
3. ride
4. win

【正解1】
4. win

【解説1】
「win」は「勝つ」という意味です。Mikaはスピーチコンテストに出て...
---
```

#### 更新コマンド
```bash
# 完全更新（推奨）
python manage.py register_grammar_fill_questions

# 部分更新（開発用）
python manage.py create_grammar_fill_questions
```

#### 処理内容
1. 既存の文法問題を全削除
2. テキストファイルから問題を読み込み
3. 正規表現で問題文、選択肢、正解、解説を抽出
4. データベースに新規登録
5. 登録件数を表示

### 会話補充問題
- **更新方式**: 部分更新（範囲指定可能）
- **データ形式**: 会話文 + 問題文 + 4選択肢 + 正解 + 解説
- **特徴**: 会話の文脈を理解する問題

### 語順選択問題
- **更新方式**: 完全更新
- **データ形式**: 語順選択肢 + 正解 + 解説
- **特徴**: 語順の理解を問う問題

### 長文読解問題
- **更新方式**: パッセージ単位で更新
- **データ形式**: 長文 + 複数問題 + 各問題の選択肢
- **特徴**: 1つのパッセージに複数問題が関連

### リスニング問題
- **更新方式**: 音声ファイル連携
- **データ形式**: 音声内容 + 問題文 + 選択肢 + 正解 + 解説
- **特徴**: 音声ファイル（MP3）と画像ファイル（PNG）が必要

## 音声・画像ファイル管理

### ファイル構造
```
static/
├── audio/
│   ├── part1/    # リスニング第1部（イラスト問題）
│   │   ├── listening_illustration_question1.mp3
│   │   ├── listening_illustration_question2.mp3
│   │   └── ...
│   ├── part2/    # リスニング第2部（会話問題）
│   │   ├── listening_conversation_question1.mp3
│   │   ├── listening_conversation_question2.mp3
│   │   └── ...
│   └── part3/    # リスニング第3部（文章問題）
│       ├── listening_passage_question1.mp3
│       ├── listening_passage_question2.mp3
│       └── ...
└── images/
    └── part1/    # リスニング第1部の画像
        ├── listening_illustration_image1.png
        ├── listening_illustration_image2.png
        └── ...
```

### ファイル配置ルール

#### 音声ファイル
- **配置先**: `static/audio/part{番号}/`
- **命名規則**: `listening_{タイプ}_question{番号}.mp3`
- **例**: `listening_illustration_question1.mp3`

#### 画像ファイル
- **配置先**: `static/images/part1/`
- **命名規則**: `listening_illustration_image{番号}.png`
- **例**: `listening_illustration_image1.png`

### 音声ファイル更新
```bash
# 音声ファイルパス更新
python manage.py update_audio_paths
```

### ファイル生成手順
1. **PDFから画像抽出**: `utils/pdf_image_extractor.py`
2. **音声ファイル生成**: `utils/text_to_speech*.py`
3. **ファイルパス更新**: `python manage.py update_audio_paths`
4. **Django静的ファイル収集**: `python manage.py collectstatic`

### 音声生成ツール
- `utils/pdf_text_extractor.py` - PDFテキスト抽出
- `utils/pdf_image_extractor.py` - PDF画像抽出
- `utils/text_to_speech.py` - リスニング第1部音声生成
- `utils/text_to_speech_conversation.py` - リスニング第2部音声生成

## 品質管理

### 1. データ検証項目
- [ ] 問題文が空でない
- [ ] 選択肢が適切な数存在する
- [ ] 正解が1つだけ存在する
- [ ] 解説が適切に設定されている
- [ ] 問題番号が連番になっている
- [ ] 音声ファイルが存在する（リスニング問題）
- [ ] 画像ファイルが存在する（リスニング第1部）

### 2. テスト手順
1. 少数の問題でテスト実行
2. フロントエンドでの表示確認
3. 解答機能の動作確認
4. 解説表示の確認
5. 音声再生の確認（リスニング問題）

## 運用フロー

### 1. 定期更新
- **頻度**: 月1回または必要に応じて
- **タイミング**: 営業時間外
- **通知**: 更新完了後にチームに通知

### 2. 緊急更新
- **手順**: バックアップ → 更新 → 検証 → 通知
- **ロールバック**: バックアップファイルからの復元

### 3. 音声ファイル更新
- **手順**: 音声生成 → ファイル配置 → パス更新 → 検証
- **ツール**: `utils/audio_generator.py`, `utils/text_to_speech_part2.py`

## 関連ファイル一覧

### データファイル
- `data/questions/grammar_fill_questions.txt`
- `data/questions/conversation_questions.txt`
- `data/questions/wordorder_questions.txt`
- `data/questions/reading_comprehesion_questions.txt`
- `data/questions/listening_illustration_questions.txt`
- `data/questions/listening_conversation_questions.txt`
- `data/questions/listening_passage_questions.txt`

### 管理コマンド
- `questions/management/commands/register_grammar_fill_questions.py`
- `questions/management/commands/register_conversation_fill_questions.py`
- `questions/management/commands/register_wordorder_fill_questions.py`
- `questions/management/commands/register_reading_comprehension_questions.py`
- `questions/management/commands/register_listening_illustration_questions.py`
- `questions/management/commands/create_listening_conversation_questions.py`
- `questions/management/commands/create_listening_passage_questions.py`

### データモデル
- `questions/models.py` - 専用モデル
- `exams/models.py` - 共通モデル

### ユーティリティ（推奨順序）

#### 主要スクリプト（必須）
1. **`utils/pdf_text_extractor.py`** - PDFテキスト抽出（最重要）
2. **`utils/pdf_image_extractor.py`** - PDF画像抽出（リスニング第1部用）
3. **`utils/text_to_speech.py`** - リスニング第1部音声生成
4. **`utils/text_to_speech_conversation.py`** - リスニング第2部音声生成

#### スクリプト整理完了
- 重複していた`audio_generator.py`と`text_to_speech_part2.py`を統合
- `text_to_speech_conversation.py`として統一
- より包括的な機能を持つスクリプトに統合

## 注意事項

### 1. データ整合性
- 既存データは完全に削除されるため、事前バックアップが必須
- 問題番号の重複チェック
- 選択肢の順序が正しいか確認

### 2. ファイル管理
- 音声ファイルと画像ファイルの同期
- ファイルパスの正確性
- ファイルサイズの最適化

### 3. パフォーマンス
- 大量データの一括更新時のメモリ使用量
- データベースのインデックス最適化
- フロントエンドの表示速度

## 更新履歴
- 2025-10-27: 初版作成（文法問題から開始）
- 2025-10-27: 全問題タイプの統合仕様書作成
- 2025-10-27: 統合仕様書に統一