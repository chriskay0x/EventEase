def set_user_role(backend, user, response, *args, **kwargs):
    """Pipeline step to assign default client role during Google Signup."""
    if backend.name == 'google-oauth2':
        if not user.role:
            user.role = 'client'
            user.save()