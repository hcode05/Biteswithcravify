def detectUser(user):
    if user.role == 1:
        return 'vendordashboard'  # name from urls.py
    elif user.role == 2:
        return 'custdashboard'    # name from urls.py
    elif user.role is None and user.is_superadmin:
        return 'admin:index'      # name for Django admin
