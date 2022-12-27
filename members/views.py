# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import UserRegisterForm, LoginForm, UserEditForm, ProfileUpdateForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from blog.models import ProfileInfo
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin

########### Register #####################################
def register(request):
    if request.user.is_anonymous:
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                if get_user_model().objects.filter(email=email):
                    return render(request, 'registration/register.html', {'form': form,'ermsg':'Enter a different Email!'})
                form.save()
                username = form.cleaned_data.get('username')
                ######################### mail system ####################################
                htmly = get_template('registration/Email.html')
                d = { 'username': username }
                subject, from_email, to = 'Welcome to Dhi Darpan', 'support@dhidarpan.com', email
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                ##################################################################
                pinstance = ProfileInfo.objects.create(user_id=request.id)
                pinstance.display_picture = '/profiles/NULL.png'
                pinstance.save()
                return redirect('login')
            else:
                return render(request, 'registration/register.html', {'form': form,'ermsgpass':'Enter a strong password!'})
        else:
            form = UserRegisterForm()
            return render(request, 'registration/register.html', {'form': form})
    return redirect('home')
  
################ Login ###################################################
def usr_login(request):
    if request.user.is_anonymous:
        if request.method == 'GET':
            lin_form = LoginForm()
            return render(request, 'registration/login.html', {'form': lin_form,'msg':''})
        else:
            lin_form = LoginForm(request.POST)
            if lin_form.is_valid():
                username = lin_form.cleaned_data.get('username')
                password = lin_form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    # Redirect to a success page.
                    return redirect('pa-land')
                else:
                    lin_form = LoginForm()
                    return render(request, 'registration/login.html', {'form': lin_form,'msg':'Username or Password is incorrect!'})
            lin_form = LoginForm()
            return render(request, 'registration/login.html', {'form': lin_form,'msg':''})
    return redirect('home')

################ Logout ###################################################
def logout_view(request):
    if request.user.is_anonymous:
        return redirect('login')
    logout(request)
    # Redirect to a success page.
    return redirect('home')

################ Validate Username ###################################################
def check_username(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if get_user_model().objects.filter(username=username):
            return HttpResponse("<div style='color:red;padding-left:2%;'><small>  Username already exists!</small></div>")
        else:
            if " " in username:
                return HttpResponse("<div style='color:red;padding-left:2%;'><small>  Username can not have Whitespaces!</small></div>")
            return HttpResponse("<div style='color:green; padding-left:2%;'><small>  Username is available!</small></div")
    return redirect('register')

################ Validate Email ###################################################
def check_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if get_user_model().objects.filter(email=email):
            return HttpResponse("<div style='color:red;padding-left:0%;'><small>  Email already exists!</small></div>")
        else:
            if "@" and "." not in email:
                return HttpResponse("<div style='color:red;padding-left:2%;'><small>  Enter Valid Email!</small></div>")
            return HttpResponse("<div style='color:green; padding-left:2%;'><small>  Email is available!</small></div")
    return redirect('register')

################ Change Password ###################################################
@login_required(login_url='/members/login/')
def change_password(request):
    if request.user.is_anonymous:
        return redirect('login')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/changepass.html', {'form': form})


################ Edit User Profile ###################################################
@login_required(login_url="/members/login/")
def edit_user_profile(request,id):
    uinstance = User.objects.get(id=id)
    user_form = UserEditForm(request.POST or None, instance=uinstance)
    if user_form.is_valid():
        email = user_form.cleaned_data.get('email')
        uobj = get_user_model().objects.get(email=email)
        if uobj.id != id:
            pinstance = ProfileInfo.objects.get(user_id=id)
            profile_form = ProfileUpdateForm(request.POST or None,request.FILES or None,instance=pinstance)
            return render(request,'registration/edit_user.html',{'user_form':user_form,'profile_form':profile_form,'ermsg':'Enter a different Email!'})
        pinstance = ProfileInfo.objects.get(user_id=id)
        profile_form = ProfileUpdateForm(request.POST or None,request.FILES or None,instance=pinstance)
        user_form.save()
    if ProfileInfo.objects.filter(user_id = id).exists():
        pinstance = ProfileInfo.objects.get(user_id=id)
        profile_form = ProfileUpdateForm(request.POST or None,request.FILES or None,instance=pinstance)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('pa-land')
    else:
        pinstance = ProfileInfo.objects.create(user_id=id)
        profile_form = ProfileUpdateForm(request.POST or None,request.FILES or None,instance=pinstance)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('pa-land')
        profile_form = ProfileUpdateForm()
    return render(request,'registration/edit_user.html',{'user_form':user_form,'profile_form':profile_form})

@login_required(login_url='/members/login/')
def deleteDp(request,uid):
    if request.method == 'DELETE':
        pi = ProfileInfo.objects.get(user_id=uid)
        pi.display_picture.delete()
        pi.display_picture = '/profiles/NULL.png'
        pi.save()
        if ProfileInfo.objects.filter(user_id = uid).exists():
            pinstance = ProfileInfo.objects.get(user_id=uid)
            profile_form = ProfileUpdateForm(request.POST or None, request.FILES or None,instance=pinstance)
        else:
            pinstance = ProfileInfo.objects.create(user_id=uid)
            profile_form = ProfileUpdateForm(request.POST or None, request.FILES or None,instance=pinstance)
        return render(request, 'registration/edit_user_model.html',{'profile_form':profile_form})
    return redirect('members/edit_user/'+str(uid))


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')
