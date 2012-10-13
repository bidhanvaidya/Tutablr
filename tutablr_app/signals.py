# in signals.py:
 
def create_profile(sender, instance, signal, created, **kwargs):
    """When user is created also create a matching profile."""
 
    from tutablr_app.models import UserProfile
 
    if created:
        UserProfile.objects.get_or_create(user = instance);
        # Do additional stuff here if needed, e.g.
        # create other required related records