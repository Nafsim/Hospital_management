from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0047_bloodtestrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicine',
            name='company',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='medicine',
            name='payment_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
