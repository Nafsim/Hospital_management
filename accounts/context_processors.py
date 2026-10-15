from django.db.models import Q
from accounts.models import Notice

def notices_context(request):
    if not request.user.is_authenticated:
        return {'notices': [], 'notice_count': 0}

    notices = []
    role = getattr(request.user, 'role', None)
    hospital = getattr(request.user, 'hospital', None)

    if role == 'hospital_admin' and hospital:
        notices = Notice.objects.filter(
            Q(hospital=hospital) | Q(hospital__isnull=True),
            status='published'
        ).order_by('-created_at')[:10]

    elif role in ['doctor', 'nurse', 'lab', 'counter', 'bloodbank', 'accountant'] and hospital:
        notices = Notice.objects.filter(
            hospital=hospital,
            status='published'
        ).order_by('-created_at')[:10]

    elif role == 'patient' and hospital:
        notices = Notice.objects.filter(
            Q(hospital=hospital) | Q(hospital__isnull=True),
            status='published'
        ).order_by('-created_at')[:10]

    elif role == 'moh':
        notices = Notice.objects.filter(status='published').order_by('-created_at')[:10]

    notices = list(notices)
    notice_count = len(notices)
    return {
        'notices': notices,
        'notice_count': notice_count,
        'lab_notices': notices,
        'lab_notice_count': notice_count,
    }




#pharmacy
def notices_context(request):
    if not request.user.is_authenticated:
        return {'notices': [], 'notice_count': 0}

    notices = Notice.objects.none()
    role = getattr(request.user, 'role', None)
    hospital = getattr(request.user, 'hospital', None)

    if role == 'hospital_admin' and hospital:
        notices = Notice.objects.filter(
            Q(hospital=hospital) | Q(hospital__isnull=True),
            status='published'
        ).order_by('-created_at')[:10]

    elif role in ['doctor', 'nurse', 'lab', 'counter', 'bloodbank', 'accountant', 'pharmacy'] and hospital:
        notices = Notice.objects.filter(
            hospital=hospital,
            status='published'
        ).order_by('-created_at')[:10]

    elif role == 'moh':
        notices = Notice.objects.filter(status='published').order_by('-created_at')[:10]

    count = notices.count() if hasattr(notices, 'count') else len(list(notices))
    return {
        'notices': notices,
        'notice_count': count,
    }