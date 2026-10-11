from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0034_doctorreferral_declined'),
        ('hospitals', '0002_hospital_city_hospital_facility_type_hospital_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(max_length=2000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('hospital', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='hospitals.hospital')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_chat_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_chat_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['hospital', 'sender', 'recipient', 'created_at'], name='accounts_ch_hospita_edee64_idx'),
        ),
    ]
