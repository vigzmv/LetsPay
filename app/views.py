import base64
import json
import random
import requests

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from .models import *
from .forms import *

state = ""

def index(request):
	return render(request,'app/home.html',{})

def register(request):
    if request.method == "POST":
        form1 = UserSignUp(request.POST, prefix="user")
        form2 = SignUpForm(request.POST, prefix="sign")
        if form1.is_valid() and form2.is_valid():
            user = form1.save(commit=False)
            user.password = make_password(form2.cleaned_data['password'])
            user.email = form2.cleaned_data['email']
            user.save()
            userprof = form2.save(commit=False)
            userprof.user = user
            userprof.save()
            return HttpResponseRedirect('/app/success')
    else:
        form1 = UserSignUp(prefix="user")
        form2 = SignUpForm(prefix="sign")

    return render(request, "app/register.html", context={'form1': form1, 'form2': form2})

def check(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    response = {}
    if user:
        response['status'] = "Not Available"
    else:
        response['status'] = "Available"
    return HttpResponse(json.dumps(response), content_type="application/json")

def success(request):
    return render(request, "app/success.html", context={})

@login_required
def createPromo(request):
	if request.method == 'POST':
		form = PromosForm(request.POST)
		if form.is_valid():
			try:
				pay_user = User.objects.get(id=request.user.id)
				user = PayUser.objects.get(user=pay_user)
			except PayUser.DoesNotExist:
				user = PayUser.objects.all().first()
			promoCode = str(request.user).upper()+"-"+str(int(form.cleaned_data['amount']))+'LP'+str(random.randint(111,999))
			try:
				while(Promos.objects.get(promoCode=promoCode)):
					promoCode += str(random.randint(111,999))
			except:
				pass
			form = form.save(commit=False)
			form.user = user
			form.promoCode = promoCode
			form.save()
			return HttpResponseRedirect('/app/success')
	else:
		form = PromosForm()
	return render(request, 'app/createPromo.html', context={'form': form})

def withdrawPromo(request):
	if request.method == 'POST':
		form = PromoWithdraw(request.POST)
		if form.is_valid():
			try:
				pay_user = User.objects.get(id=request.user.id)
				user = PayUser.objects.get(user=pay_user)
			except PayUser.DoesNotExist:
				user = PayUser.objects.all().first()
			promoCode = form.cleaned_data['promoCode']
			p = Promos.objects.get(promoCode=promoCode)
			p.active = False
			p.save()
			return HttpResponseRedirect('/app/')
	else:
		form = PromoWithdraw()
	return render(request, 'app/withdrawPromo.html', context={'form': form})

@csrf_exempt
def sendOtp(request):
	url = "https://accounts-uat.paytm.com/signin/otp"
	print request.body[6:]
	if request.method != "POST":
		return JsonResponse({'status':'FAILURE'})
	payload = "{\n\"phone\":\""+ request.body[6:] +"\",\n\"clientId\":\"staging-grofers\",\n\"scope\":\"wallet\",\n\"responseType\":\"token\"\n}"
	headers = {
	    'content-type': "application/json"
	    }

	response = requests.request("POST", url, data=payload, headers=headers)
	response = response.json()
	print response
	global state
	state = str(response['state'])
	print state
	return JsonResponse({'state': response['state']})

@csrf_exempt
def get_token(request):
	global state
	url = "https://accounts-uat.paytm.com/signin/validate/otp"
	if request.method != "POST":
		return JsonResponse({'status':'FAILURE'})
	payload = "{\"otp\":\"" + request.body[4:] +"\",\"state\":\"" + state + "\"}"
	print request.body[4:10]
	print payload

	headers = {
	    'content-type': "application/json",
	    "authorization": "Basic c3RhZ2luZy1ncm9mZXJzOjUxZTZkMDk2LTU2ZjYtNDBiNC1hMmI5LTllMGY4ZmE3MDRiOA=="
	    }

	response = requests.request("POST", url, data=payload, headers=headers)
	response = response.json()
	print response
	return JsonResponse({'access_token': response['access_token']})
