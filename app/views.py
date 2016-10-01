import json
import random

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import *
from .forms import *

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
