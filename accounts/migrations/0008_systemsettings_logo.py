# Generated manually to add logo field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemsettings',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logos/'),
        ),
    ]
