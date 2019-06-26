from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_integer
from .models import Photo, Photo_info
from serendipity.settings import *
import os
from datetime import datetime, timedelta
import random
import string

from decouple import config

import sys
from sdk.api.message import Message
from sdk.exceptions import CoolsmsException



def index(request):
    return render(request, 'main_page/index.html')



def upload(request):
    if request.method=="POST":
        if not os.path.exists(MEDIA_ROOT):
            os.mkdir(MEDIA_ROOT)
        path = os.path.join(MEDIA_ROOT, 'files')
        if not os.path.exists(path):
            os.mkdir(path)
        path2 = os.path.join(path, str(request.user.pk))
        if not os.path.exists(path2):
            os.mkdir(path2)
        if Photo.objects.all().count()==0:
            upload_num =0
        else:
            p = Photo.objects.all().last()
            last_upload_num = p.upload_num
            upload_num = last_upload_num+1
        print(f'upload_num: {upload_num}')
        if 'upload' in request.POST:
            file_list = request.FILES.getlist('img_files')
            if not file_list:
                return render(request, 'main_page/upload.html')
            else:
                for file in request.FILES.getlist('img_files'):

                    LENGTH = 15
                    # 숫자 + 대소문자
                    string_pool = string.ascii_letters + string.digits

                    # 랜덤한 문자열 생성
                    url_ran = ""
                    for i in range(LENGTH):
                        # 랜덤한 문자열 하나 선택
                        url_ran += random.choice(string_pool)
                    print(url_ran)
                    p = Photo(photo=file, from_user=request.user, upload_num = upload_num, random_url=url_ran)
                    p.save()

                print("redirect delete")

                return redirect('main:delete', upload_num)


    return render(request,'main_page/upload.html')


def delete(request, upload_num):
    if request.method == "POST":
        if 'delete' in request.POST:
            cbox_list = request.POST.getlist('cbox')

            for photo_pk in cbox_list:
                photo = Photo.objects.get(pk=photo_pk)
                photo.delete()

        elif 'next' in request.POST:
            cbox_list = request.POST.getlist('cbox')
            if cbox_list:
                photos = Photo.objects.filter(from_user=request.user, msg_flag=False, upload_num=upload_num).order_by('-pk')
                for photo in photos:
                    if str(photo.pk) not in cbox_list:
                        photo.delete()
                return redirect('main:set_phone_number', upload_num)

    photos = Photo.objects.filter(from_user=request.user,msg_flag=False, upload_num=upload_num).order_by('-pk')

    context = {'photos': photos}
    return render(request, 'main_page/delete.html', context)


def set_phone_number(request,upload_num):
    photos = Photo.objects.filter(from_user=request.user, msg_flag=False, upload_num=upload_num)
    print(photos)
    if request.method == "POST":
        period = request.POST.get('period')
        try:
            validate_integer(period)
        except:
            print("error")
            msg='기간은 숫자로만 입력해야합니다.'
            context={'msg':msg,
                     'upload_num':upload_num}
            return render(request, 'main_page/message.html',context)
        phone_from = request.POST.get('phone_from')

        random_day = random.choice(range(0, int(period)+1))
        now = datetime.now()
        td = timedelta(days=random_day, minutes=3)
        random_date = now + td
        print(f'now: {now}, random_day={random_day}, random_date={random_date}')
        print(random_date)

        from_name = request.POST.get('from_name')
        phone_to = request.POST.get('phone_to')
        try:
            validate_integer(phone_to)
        except:
            msg='핸드폰은 숫자로만 입력해야합니다.'
            context={'msg':msg,
                     'upload_num':upload_num}
            return render(request, 'main_page/message.html',context)
        if len(phone_to) <11:
            msg = '핸드폰 번호를 11자 입력해주세요.'
            context = {'msg': msg,
                       'upload_num':upload_num}
            return render(request, 'main_page/message.html', context)
        to_name = request.POST.get('to_name')
        message = request.POST.get('message')
        if len(message) > 40:
            msg = '메시지를 40자 이내로 입력해주세요.'
            context = {'msg': msg,
                       'upload_num':upload_num}
            return render(request, 'main_page/message.html', context)
        photo_info = Photo_info(send_date=random_date, phone_from=phone_from, phone_to=phone_to,from_name=from_name,to_name=to_name, message=message, period=period)
        photo_info.save()
        photos = Photo.objects.filter(from_user=request.user, msg_flag=False, upload_num=upload_num)
        print(f'photos: {len(photos)}')
        rd = random.choice(range(0,len(photos)))
        photos[rd].info=photo_info
        photos[rd].save()

        return redirect('main:confirm', upload_num)

    return render(request,'main_page/set_phone_number.html')



def confirm(request, upload_num):
    photos = Photo.objects.filter(from_user=request.user, msg_flag=False, upload_num=upload_num)
    print(photos)
    if request.method == "POST":
        if 'edit' in request.POST:
            return redirect('main:edit', upload_num)
        elif 'confirm' in request.POST:
            for photo in photos:
                if photo.info is not None:
                    photo.msg_flag = True
                    photo.save()
                    send_sms(photo)
                else:
                    photo.delete()
            msg = "성공적으로 보내졌습니다."
            context={'msg':msg,}
            print(msg)
            return render(request, 'main_page/message.html', context)

    info_list = []
    for photo in photos:
        print(photo.info)
        if photo.info is not None:
            info=photo.info
    print(f'info: {info}')
    context={'photos':photos, 'info': info}
    return render(request,'main_page/confirm.html',context)


def edit(request, upload_num):
    photos = Photo.objects.filter(from_user=request.user, msg_flag=False, upload_num=upload_num)
    info_list = []
    for photo in photos:
        print(photo.info)
        if photo.info is not None:
            info=photo.info
    if request.method =="POST":
        period = request.POST.get('period')
        try:
            validate_integer(period)
        except:
            print("error")
            msg='기간은 숫자로만 입력해야합니다.'
            context={'msg':msg}
            return render(request, 'main_page/message.html',context)
        from_name = request.POST.get('from')
        random_day = random.choice(range(0, int(period) + 1))
        now = datetime.now()
        td = timedelta(days=random_day, minutes=3)
        random_date = now + td

        phone_to = request.POST.get('phone_to')
        try:
            validate_integer(phone_to)
        except:
            msg='핸드폰은 숫자로만 입력해야합니다.'
            context={'msg':msg}
            return render(request, 'main_page/message.html',context)
        if len(phone_to) <11:
            msg = '핸드폰 번호를 11자 입력해주세요.'
            context = {'msg': msg}
            return render(request, 'main_page/message.html', context)

        to_name = request.POST.get('to_name')
        message = request.POST.get('message')
        if len(message) > 40:
            msg = '메시지를 40자 이내로 입력해주세요'
            context = {'msg': msg}
            return render(request, 'main_page/message.html', context)
        info.period = period
        info.phone_to= phone_to
        info.to_name = to_name
        info.message = message
        info.send_date = random_date
        info.save()

        return redirect('main:confirm', upload_num)
    context = {'info': info}
    return render(request,'main_page/edit.html',context)


def send_sms(photo):
    api_key = config('api_key')
    api_secret = config('api_secret')

    print(photo.info)
    date = photo.info.send_date
    print(f'date:{date}')
    dt=date.strftime('%Y%m%d%H%M')
    print(f'dt : {dt}')
    #dt = date.year + datetime.month + datetime.day + datetime.hour + datetime.minute
    #print(dt)

    # 4 params(to, from, type, text)설정
    params = dict()
    params['type'] = 'sms'  # Message type ( sms, lms, mms, ata )
    params['to'] = photo.info.phone_to  # 받는사람번호(,로 추가가능)
    params['from'] = '01074210136'  # 보내는사람번호(coolsms사이트에 등록되어있어야함)
    params['text'] = 'Test Message'  # 보내는 메세지
    params['datetime'] = dt
    cool = Message(api_key, api_secret)

    # error 확인
    try:
        response = cool.send(params)
        print("Success Count : %s" % response['success_count'])
        print("Error Count : %s" % response['error_count'])
        print("Group ID : %s" % response['group_id'])
        if "error_list" in response:
            print("Error List : %s" % response['error_list'])

    except CoolsmsException as e:
        print("Error Code : %s" % e.code)
        print("Error Message : %s" % e.msg)

def photo(request, pk, random_url):
    photo = Photo.objects.get(pk=pk, random_url=random_url)
    date = photo.created_at
    dt = date.strftime('%Y-%m-%d %H:%M')

    context = { 'photo':photo,
                'dt':dt }
    return render(request, 'main_page/photo_2.html', context)

def main(request):
    return render(request, 'main_page/home.html')


def use(request):
    return render(request, 'main_page/use.html')