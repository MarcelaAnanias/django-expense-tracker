from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from validate_email import validate_email
from django.contrib import messages
from django.contrib import auth
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import account_activation_token

# Create your views here.


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'This email is already taken. Please choose a different one.'}, status=409)
        return JsonResponse({'username_valid': True})
    
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'This name is already taken. Please choose a different one.'}, status=409)
        return JsonResponse({'email_valid': True})

class RegistrationView(View):
    def get(self, request):
        return render(request,'authentication/register.html')
    
    def post(self, request):

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():

                if len(username)<4:
                    messages.error(request, 'Username too short')
                    return render(request,'authentication/register.html', context)

                if len(password)<6:
                    messages.error(request, 'Password too short')
                    return render(request,'authentication/register.html', context)
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)

                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }

                link = reverse('activate', kwargs={'uidb64': email_body['uid'], 'token': email_body['token']})
                
                email_subject = 'Activate your account'

                activate_url = 'http://'+current_site.domain+link

                email = EmailMessage (
                    email_subject,
                    'Hi '+user.username + ', Please the link below to activate your account \n'+activate_url,
                    "noreply@themoney.com",
                    [email],
                )

                email.send(fail_silently=False)
                messages.success(request, 'Your account has been created! Check your email to continue.')
                return render(request, 'authentication/register.html')

        return render(request,'authentication/register.html')
    
class VerificationView(View):
    def get(self, request, uidb64, token):

        try:
            id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

        except Exception as ex:
            pass

        return redirect('login')
    
class LoginView(View):
    def get(self, request):
        return render(request,'authentication/login.html')
    
    def post(self, request):
        username=request.POST['username']
        password=request.POST['password']

        if username and password:
            user=auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, '+user.username+' you are now logged in')
                    return redirect('expenses')
            
                messages.error(request, 'Account is not active, please check your email')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html')
        messages.error(request, 'Please fill all fields')
        return render(request, 'authentication/login.html')
    
class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')