from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(text, filename, size=(400, 300)):
    # 画像を作成
    image = Image.new('RGB', size, color='lightgray')
    draw = ImageDraw.Draw(image)
    
    # フォントを設定（日本語フォントを使用）
    try:
        font = ImageFont.truetype("Arial", 24)
    except:
        font = ImageFont.load_default()
    
    # テキストを描画
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, font=font, fill='black')
    
    # 画像を保存
    os.makedirs('media/question_images', exist_ok=True)
    image.save(f'media/question_images/{filename}')

# プレースホルダー画像を生成
illustrations = [
    ('illustration1.jpg', 'Boy playing soccer'),
    ('illustration2.jpg', 'Cat on the chair'),
    ('illustration3.jpg', 'Sunny weather'),
    ('illustration4.jpg', 'Clock showing 3 o\'clock'),
    ('illustration5.jpg', 'Girl in red dress'),
    ('illustration6.jpg', 'Book and pen on table'),
    ('illustration7.jpg', 'Dog in the park'),
    ('illustration8.jpg', 'Boy eating apple'),
    ('illustration9.jpg', 'School next to park'),
    ('illustration10.jpg', 'Family having dinner')
]

for filename, text in illustrations:
    create_placeholder_image(text, filename)
    print(f'Created {filename}') 