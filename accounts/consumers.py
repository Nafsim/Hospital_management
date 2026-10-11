import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from django.db.models import Q

from .models import ChatMessage, DoctorPatient, PatientAppointment, User


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        self.target = await self.get_target(user, self.scope['url_route']['kwargs']['user_id'])
        if not user or not user.is_authenticated or not self.target:
            await self.close(code=4403)
            return

        ids = sorted([user.id, self.target.id])
        self.room_group_name = f'chat_{ids[0]}_{ids[1]}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def receive_json(self, content, **kwargs):
        body = str(content.get('body', '')).strip()
        if not body or len(body) > 2000:
            return

        message = await self.save_message(self.scope['user'], self.target, body)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'body': message.body,
                    'sender_id': message.sender_id,
                    'sender_name': (
                        message.sender.get_full_name()
                        or message.sender.username
                    ),
                    'created_at': timezone.localtime(
                        message.created_at
                    ).strftime('%d %b %Y, %I:%M %p'),
                    'attachment_url': message.attachment.url if message.attachment else '',
                    'attachment_name': message.attachment_name,
                },
            },
        )

    async def chat_message(self, event):
        await self.send_json(event['message'])

    @database_sync_to_async
    def get_target(self, user, user_id):
        if not user or not user.is_authenticated:
            return None
        if user.role not in ('doctor', 'patient'):
            return None
        if user.role == 'doctor':
            patient_codes = DoctorPatient.objects.filter(
                doctor=user,
            ).values_list('patient_id', flat=True)
            appointment_patient_ids = PatientAppointment.objects.filter(
                doctor=user,
            ).exclude(status='cancelled').values_list('patient_user_id', flat=True)
            return User.objects.filter(
                id=user_id,
                role='patient',
                is_active=True,
            ).filter(
                Q(patient_profile__patient_id__in=patient_codes) |
                Q(id__in=appointment_patient_ids)
            ).exclude(id=user.id).first()
        appointment_doctor_ids = PatientAppointment.objects.filter(
            patient_user=user,
        ).exclude(status='cancelled').values_list('doctor_id', flat=True)
        return User.objects.filter(
            id=user_id,
            role='doctor',
            id__in=appointment_doctor_ids,
            is_active=True,
        ).exclude(id=user.id).first()

    @database_sync_to_async
    def save_message(self, sender, recipient, body):
        hospital_id = None
        if sender.role == 'doctor':
            relation = DoctorPatient.objects.filter(
                doctor=sender,
                patient_id=recipient.patient_profile.patient_id,
            ).first()
            if relation:
                hospital_id = relation.hospital_id
        appointment = PatientAppointment.objects.filter(
            **(
                {'doctor': sender, 'patient_user': recipient}
                if sender.role == 'doctor'
                else {'patient_user': sender, 'doctor': recipient}
            )
        ).first()
        if hospital_id is None and appointment:
            hospital_id = appointment.hospital_id
        if hospital_id is None:
            hospital_id = recipient.hospital_id or sender.hospital_id
        return ChatMessage.objects.create(
            hospital_id=hospital_id,
            sender=sender,
            recipient=recipient,
            body=body,
        )
