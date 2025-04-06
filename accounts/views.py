from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from core.models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from accounts.forms import ContactForm
from django.core.mail import send_mail
from django.http import HttpResponse

# Create your views here.
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        messages.info(request,"Login Failed, Please Try Again")
    return render(request,'accounts/login.html')


def user_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone = request.POST.get('phone_field')
        # print(username,email)
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request,"Username already Exists!")
                return redirect('user_register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.info(request,"Email already Exists!")
                    return redirect('user_register')
                else:
                    user = User.objects.create_user(username=username,email=email,password=password)
                    user.save()
                    data = Customer(user = user,phone_field=phone)
                    data.save()
                    # Code for Login of user will come here
                    our_user = authenticate(username=username,password=password)
                    if our_user is not None:
                        login(request,user)
                        return redirect('/')
        else:
            messages.info(request,"Password and Confirm Password Mismatch!")
            return redirect('user_register')
    return render(request,'accounts/register.html')


def user_logout(request):
    logout(request)
    return redirect('/')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Handle the form submission (e.g., send an email)
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            phone = form.cleaned_data['phone']

            # Send email (you can customize the email sending logic as needed)
            send_mail(
                f"Contact Message from {name}",
                message + f"\n\nPhone: {phone}",
                email,  # From email address
                ['rochaksulu2002@gmail.com'],  # Recipient email address
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully.')

            # Return a success response (or redirect to a thank you page)
            return redirect('/')
    else:
        form = ContactForm()

    return render(request, 'accounts/contact.html', {'form': form})
