from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0009_tour_is_featured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
