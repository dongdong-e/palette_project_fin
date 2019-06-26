from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm

from .forms import UserCustomCreationForm
# 비밀번호 변경 후, 로그인을 유지하기 위한 함수 import
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout


## 회원가입
def signup(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    if request.method == 'POST':
        form = UserCustomCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(user)
            # 회원가입 후 로그인 상태 유지하기
            auth_login(request, user)
            return redirect('main:index')

    else:
        form = UserCustomCreationForm()
    context = {'form':form}
    return render(request, 'account/signup.html', context)


## 로그인
def login(request):
    if request.user.is_authenticated:
        return redirect('main:index')

    if request.method == 'POST':
        # AuthenticationForm: 로그인 Form
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            # form.get_user(): user의 정보가 담겨 있음
            auth_login(request, form.get_user())
            return redirect(request.GET.get('next') or 'main:index')
    else:
        form = AuthenticationForm()
    context = {'form':form}
    return render(request, 'account/login.html', context)


## 로그아웃
@login_required
def logout(request):
    auth_logout(request)
    return redirect('main:index')


## 회원정보 수정
def edit(request):
    if request.method == 'POST':
        form = UserCustomChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('boards:index')
    else:
        form = UserCustomChangeForm(instance=request.user)
    context = {'form':form}
    return render(request, 'accounts/accounts_form.html', context)


## 비밀번호 변경
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # 비밀번호 변경 후에도 로그인 상태 유지
            # 회원가입 후에 로그인 유지하는 것과 비슷함: signup 참고
            update_session_auth_hash(request, user)
            return redirect('boards:index')
    else:
        form = PasswordChangeForm(request.user)
    context = {'form':form}
    return render(request, 'accounts/accounts_form.html', context)


## 회원탈퇴
def delete(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('boards:index')
    else:
        return redirect('boards:index')