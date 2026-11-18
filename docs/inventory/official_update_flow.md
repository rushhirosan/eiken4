# 公式過去問が更新されたとき / 網羅を厚くするとき

公開への **再取り込み（PDF → register → サイト）はしない**。  
やることは「傾向を更新 → 足りない型を original で自作 → 機械酷似 → **人は品質チェック**」。

## 手順

1. **（任意）PDF を保管**  
   `data/pdf_import/{level}_kakomon/` などへ置く。配信・公開登録には使わない。

2. **保管 txt を必要なら更新**  
   機械の酷似チェック・inventory の入力は級別 txt（`data/questions/`）。  
   最新回を比較コーパスに載せたいときだけ更新する（手置き or `utils/legacy/`。**`register_*` で公開しない**）。

3. **inventory を再生成**

   ```bash
   python scripts/gen_inventory.py --level 3   # または 4 / 5 / --all
   ```

4. **穴を決める**  
   `docs/inventory/level{N}/` の該当カテゴリ（焦点・談話機能・網羅メモ）を見る。  
   「original に足りない型」を 1〜数個メモする。公式本文を開いて類題を作らない。  
   任意（L の疑問詞焦点）:

   ```bash
   python scripts/check_inventory_coverage.py --level 4
   ```

5. **original を自作**  
   `eiken-original-authoring`（`references/*.md` の枠）。置き場は `data/questions/original/level{N}/` のみ。

6. **機械レビュー**  
   - 酷似: `eiken-originality-review`（級別 txt。PDF は開かない）  
   - 解説: `eiken-explanation-quality-review`  
   - 品質: `eiken-question-quality-review`  
   - 語順など: `validate_*` / preflight

7. **人の時間（メイン）**  
   作問後の**問題チェック**に使う（解けるか、空所論理、ダミー、解説、級適合、ポイント）。  
   公式 PDF と全問並べる酷似目視は **しない／ごく軽く**（機械が怪しい番号・最新回の抜けだけ）。

8. **公開前チェック → 登録**  
   `.cursor/rules/original-questions.mdc` を通してから `--original` 登録。

## 役割分担

| 役割 | 担当 |
|------|------|
| 傾向・網羅の穴 | inventory（`gen_inventory`） |
| 公式文との類似 | 機械（級別 txt） |
| 作問後の中身 | **人（主）** |
| 公式 PDF 酷似 | 人は軽く／疑わしいときだけ |
