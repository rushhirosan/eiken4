from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0022_add_writing_question_type_and_writing_user_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='content',
            field=models.TextField(max_length=5000, verbose_name='内容'),
        ),
    ]
