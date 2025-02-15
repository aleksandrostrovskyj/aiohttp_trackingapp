import db
from security import check_password_hash


async def validate_login_form(conn, form, csrf_token):

    username = form['username']
    password = form['password']

    if form['csrfmiddlewaretoken'] != csrf_token:
        return 'Invalid csrf_token'

    user = await db.get_user_by_name(conn, username)

    if not user:
        return 'Invalid username'
    if not check_password_hash(password, user['password_hash']):
        return 'Invalid password'
    else:
        return None

    return 'error'
