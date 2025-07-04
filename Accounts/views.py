from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationForm, UserUpdateForm, DepositMoneyForm
from django.views.generic import FormView
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from Book.models import Purchase
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import UserAccount
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_user_email(
    subject, action, book_title, user, balance=None, title=None, amount=None):
    date = user.date_joined.strftime("%Y-%m-%d")
    context = {
        "subject": subject,
        "action": action,
        "book_title": book_title,
        "user": user,
        "date": date,
        "balance": balance,
        "title": title,
        "amount": amount,
    }
    email_subject = f"{subject} | Noor Library"
    html_message = render_to_string("accounts/email.html", context)

    email = EmailMultiAlternatives(subject=email_subject, body="", to=[user.email])
    email.attach_alternative(html_message, "text/html")
    email.send()


class UserRegistrationView(FormView):
    template_name = "accounts/registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LoginView(LoginView):
    template_name = "accounts/login.html"
    title = "Login"

    def get_success_url(self):
        return reverse_lazy("profile")


def LogoutView(request):
    logout(request)
    return redirect("login")


class UserProfileView(View):
    template_name = "accounts/profile.html"
    title = "Profile"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        purchases = Purchase.objects.filter(user=request.user).order_by(
            "-purchase_date"
        )
        return render(
            request, self.template_name, {"user": request.user, "purchases": purchases}
        )


class UserUpdateView(View):
    template_name = "accounts/update_profile.html"
    title = "Update Profile"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
        return render(request, self.template_name, {"form": form})


class DepositMoneyView(LoginRequiredMixin, FormView):
    template_name = "book/deposit_money.html"
    form_class = DepositMoneyForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        amount = form.cleaned_data["balance"]

        user_account = self.request.user.account  # OneToOneField assumed
        user_account.balance += amount
        user_account.save(update_fields=["balance"])

        messages.success(self.request, f"Successfully deposited {amount} units.")
        send_user_email(
            subject="Deposit Successful",
            action="deposit",
            book_title=None,
            user=self.request.user,
            balance=user_account.balance,
            amount=amount,
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please enter a valid deposit amount.")
        return super().form_invalid(form)
