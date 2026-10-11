from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0033_medicalrecord_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorreferral',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('accepted', 'Accepted'),
                    ('declined', 'Declined'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
