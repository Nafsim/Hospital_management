from django.db.models import Q
from accounts.models import Notice


def notices_context(request):
    if not request.user.is_authenticated:
        return {'notices': []}

    if request.user.role == 'hospital_admin' and request.user.hospital:
        # Hospital Admin → own hospital notices + MOH notices
        notices = Notice.objects.filter(
            Q(hospital=request.user.hospital) | Q(hospital__isnull=True),
            status='published'
        ).order_by('-created_at')[:10]

    elif request.user.role in ['doctor', 'nurse', 'lab', 'counter', 'bloodbank', 'accountant'] and request.user.hospital:
        # Doctor / Nurse / Staff → only their hospital notices
        notices = Notice.objects.filter(
            hospital=request.user.hospital,
            status='published'
        ).order_by('-created_at')[:10]

    elif request.user.role == 'moh':
        # MOH → all notices
        notices = Notice.objects.filter(status='published').order_by('-created_at')[:10]

    else:
        notices = []

    return {'notices': notices}
