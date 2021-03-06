"""
eLCID specific views.
"""
import csv
import random

from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.generic import TemplateView, FormView, View

import letter
from letter.contrib.contact import EmailForm, EmailView


from opal.core import application

from elcid.forms import BulkCreateUsersForm

app = application.get_app()
u = unicode
POSTIE = letter.DjangoPostman()


def temp_password():
    num = random.randint(10, 99)
    word = random.choice(['womble', 'bananas', 'flabbergasted', 'kerfuffle'])
    return '{0}{1}'.format(num, word)


class Error500View(View):
    """
    Demonstrative 500 error to preview templates.
    """
    def get(self, *args, **kwargs):
        if self.request.META['HTTP_USER_AGENT'].find('Googlebot') != -1:
            return HttpResponse('No')
        raise Exception("This is a deliberate error")


class BulkCreateUserView(FormView):
    """
    Used in the admin - bulk create users.
    """
    form_class = BulkCreateUsersForm
    template_name = 'admin/bulk_create_users.html'
    success_url = '/admin/auth/user/'

    def form_valid(self, form):
        """
        Create the users from our uploaded file!

        Arguments:
        - `form`: Form

        Return: HTTPResponse
        Exceptions: None
        """
        usernames = [u.username for u in User.objects.all()]
        new_users = []

        for row in csv.reader(form.cleaned_data['users']):
            email = row[0]
            name_part, _ = email.split('@')

            # Check for reused usernames
            if name_part in usernames:
                form._errors['users'] = form.error_class(['Some of those users already exist :('])
                del form.cleaned_data['users']
                return self.form_invalid(form)

            frist, last = name_part.split('.')
            user = User(username=name_part,
                        email=email,
                        first_name=frist,
                        last_name=last,
                        is_active=True,
                        is_staff=False,
                        is_superuser=False)
            user.tp = temp_password()
            user.set_password(user.tp)
            new_users.append(user)

        for u in new_users:
            u.save()

        return super(BulkCreateUserView, self).form_valid(form)


class ElcidTemplateView(TemplateView):
    def dispatch(self, *args, **kwargs):
        self.name = kwargs['name']
        return super(ElcidTemplateView, self).dispatch(*args, **kwargs)

    def get_template_names(self, *args, **kwargs):
        return ['elcid/modals/'+self.name]

    def get_context_data(self, *args, **kwargs):
        ctd = super(ElcidTemplateView, self).get_context_data(*args, **kwargs)

        try:
            ctd["model"] = apps.get_model(app_label='elcid', model_name=self.name)
        except LookupError:
            pass

        return ctd
