from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model

class UserCustomCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['username', 'phone_number', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '15자 이내로 입력 가능합니다.'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01012345678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@serendipity.com'}),
        }
        labels = {
            'username': '아이디',
            'phone_number': '핸드폰 번호',
            'email': '이메일',
        }

    # 글자수 제한
    def __init__(self, *args, **kwargs):
        super(UserCustomCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['maxlength'] = 15