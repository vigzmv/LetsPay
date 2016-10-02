import base64
import collections
import json
import random
import requests
import uuid

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from .models import *
from .forms import *
from Checksum import generate_checksum

state = ""
access_token = ""
checksumHash = ""
data_dict = collections.OrderedDict()

def __get_param_string__(params):
    params_string = []
    for key in sorted(params.iterkeys()):
        value = params[key]
        params_string.append('' if value == 'null' else str(value))
    return '|'.join(params_string)

def index(request):
	if request.user.is_authenticated and not request.user.is_superuser:
		pay_user = User.objects.get(id=request.user.id)
		user = PayUser.objects.get(user=pay_user)
		promos = Promos.objects.filter(user=user)
		context = {'promoCodes': promos}
	else:
		context = {}
	return render(request,'app/home.html', context=context)

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
	global access_token
	access_token = response['access_token']
	return JsonResponse({'access_token': response['access_token']})

@csrf_exempt
def checkBalance(request):
	global access_token
	url = "http://trust-uat.paytm.in/wallet-web/checkBalance"

	if request.method != "POST":
		return JsonResponse({'status': 'FAILURE'})
	headers = {
		'ssotoken' : access_token
	}
	response = requests.request("POST", url, headers=headers)
	# print response.json()
	response = response.json()
	print response

	return JsonResponse({'balance': response['response']['amount']})

def generateChecksum(request):
	global checksumHash
	global data_dict
	if request.method != "GET":
		return JsonResponse({'status': 'FAILURE'})

	MERCHANT_KEY = 'hwPPuQZBD8ZMbhPM';
	data_dict = {
    	'MID':'PayAUT78996357564502',
    	'ORDER_ID': str(uuid.uuid4().fields[-1])[:9],
    	'TXN_AMOUNT': request.body[7:],
    	'CUST_ID':'acfff@paytm.com',
    	'INDUSTRY_TYPE_ID':'Retail',
    	'WEBSITE':'PaySeam',
    	'CHANNEL_ID':'WEB',
	    #'CALLBACK_URL':'http://localhost/pythonKit/response.cgi',
    }
	checksumHash = generate_checksum(data_dict, MERCHANT_KEY)
	print checksumHash
	print "OrderId = ", data_dict['ORDER_ID']
	data_dict['CHECKSUMHASH'] = checksumHash

	print data_dict

	return JsonResponse({'status': 'SUCCESS'})

@csrf_exempt
def makeTransaction(request):
	global data_dict

	dict_string = __get_param_string__(data_dict)

	encoded = base64.b64encode(dict_string)

	url = "https://pguat.paytm.com/oltp/HANDLER_FF/withdrawScw?JsonData="+encoded

	print url

	response = requests.request("POST", url)

	response = response.json()

	print response
	if response['Error'] != None:
		response['status'] = "FAILURE"

	return JsonResponse({'status': response['status']})
