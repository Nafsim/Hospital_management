from accounts.models import Notice

def notices_context(request):
    if not request.user.is_authenticated:
        return {}
    
    notices = Notice.objects.filter(status='published')[:5]
    
    return {'notices': notices}
