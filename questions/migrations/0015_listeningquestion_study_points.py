from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0014_readingquestion_study_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='listeningquestion',
            name='study_points',
            field=models.JSONField(
                blank=True,
                help_text='学習ポイント（category / title / keys のdict）。ノート・振り返り用',
                null=True,
            ),
        ),
    ]
