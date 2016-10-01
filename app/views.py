import json

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
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
