"""Our pluggable views."""


from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
)
from flask.ext.login import login_user

from . import StormpathError
from .models import User


def register():
    """
    Register a new user with Stormpath.

    This view will render a registration template, and attempt to create a new
    user account with Stormpath.

    The fields that are asked for, the URL this view is bound to, and the
    template that is used to render this page can all be controlled via
    Flask-Stormpath settings.
    """
    data = {
        'username': None,
        'email': None,
        'password': None,
        'given_name': None,
        'middle_name': None,
        'surname': None,
    }

    # If we receive a POST request, it means a user is attempting to register
    # on our site.
    if request.method == 'POST':

        # Iterate through all fields, grabbing the necessary form data and
        # flashing error messages if required.
        for field in data.keys():
            if current_app.config['STORMPATH_ENABLE_%s' % field.upper()]:
                data[field] = request.form.get(field)
                if current_app.config['STORMPATH_REQUIRE_%s' % field.upper()] and not data[field]:
                    flash('%s is required.' % field.replace('_', ' ').title())

        # Attempt to create the user's account on Stormpath.
        try:

            # Since Stormpath requires both the given_name and surname fields
            # be set, we'll just set the both to 'Anonymous' if the user has
            # explicitly said they don't want to collect those fields.
            data['given_name'] = data['given_name'] or 'Anonymous'
            data['surname'] = data['given_name'] or 'Anonymous'

            # Create the user account on Stormpath.  If this fails, an
            # exception will be raised.
            account = User.create(**data)

            # If we're able to successfully create the user's account, we'll
            # log the user in (creating a secure session using Flask-Login),
            # then redirect the user to the ?next=<url> query parameter, or the
            # STORMPATH_REDIRECT_URL setting.
            login_user(account, remember=True)

            return redirect(request.args.get('next') or current_app.config['STORMPATH_REDIRECT_URL'])
        except StormpathError, err:
            flash(err.user_message)

    return render_template(current_app.config['STORMPATH_REGISTRATION_TEMPLATE'])
