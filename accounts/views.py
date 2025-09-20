from django.contrib.auth import login
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import EmailAuthenticationForm, RegistrationForm


class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('for_reinhardt')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LoginView(DjangoLoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy('accounts:login')
