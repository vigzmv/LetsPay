import base64
import collections
import json
import random
import requests
import urllib
import urlparse
import uuid

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from .models import *
from .forms import *
from Checksum import generate_checksum, generate_checksum_by_str, verify_checksum

state = ""
phone = ""
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
	print request.user
	if request.user.is_authenticated and not request.user.is_superuser and not request.user.is_anonymous:
		pay_user = User.objects.get(id=request.user.id)
		user = PayUser.objects.get(user=pay_user)
		promos = Promos.objects.filter(user=user)
		list1 = promos.objects.filter(active=True).order_by('-created')
		print list1
		list2 = promos.objects.filter(active=False).order_by('-created')
		print list2
		list1.append(list2)
		print list1
		context = {'lists': list1}
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

def success1(request):
    return render(request, "app/success1.html", context={})

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
			return HttpResponseRedirect('/app/success1')
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
	global phone
	phone = request.body[6:]
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

	MERCHANT_KEY = '0aO3vzgaGK6zc%fo';
	data_dict = {
    	'MID':'Payaut54959786493007',
    	'ORDER_ID': str(uuid.uuid4().fields[-1])[:9],
    	'TXN_AMOUNT': str(request.GET.get('amount')),
    	'CUST_ID':str(uuid.uuid4().fields[-1])[:9],
    	'INDUSTRY_TYPE_ID':'Retail',
    	'WEBSITE':'AutoDebit',
    	'CHANNEL_ID':'WEB',
    	"ReqType" : "WITHDRAW",
    	"AppIP" : "0.0.0.0",
    	"Currency" : "INR",
    	"DeviceId" : str(phone),
    	"SSOToken" : str(access_token),
    	"PaymentMode" : "PPI",
		"AuthMode" : "USRPWD"
	    #'CALLBACK_URL':'http://localhost/pythonKit/response.cgi',
    }
	checksumHash = generate_checksum(data_dict, MERCHANT_KEY)
	print checksumHash
	print "OrderId = ", data_dict['ORDER_ID']
	data_dict['CheckSum'] = checksumHash

	print data_dict

	verify = verify_checksum(data_dict, MERCHANT_KEY, data_dict['CheckSum'])
	print verify
	print data_dict

	return JsonResponse({'status': 'SUCCESS'})

@csrf_exempt
def makeTransaction(request):
	global data_dict

	# print data_dict

	# trans_dict = {
	# 	"MID" : data_dict['MID'],
	# 	"ReqType" : "WITHDRAW",
	# 	"TxnAmount" : str(data_dict['TXN_AMOUNT']),
	# 	"AppIP" : "0.0.0.0",
	# 	"OrderId" : data_dict['ORDER_ID'],
	# 	"Currency" : "INR",
	# 	"DeviceId" : str(phone),
	# 	"SSOToken" : str(access_token),
	# 	"PaymentMode" : "PPI",
	# 	"CustId" : str(data_dict['CUST_ID']),
	# 	"IndustryType" : "Retail",
	# 	"Channel" : "WEB",
	# 	"AuthMode" : "USRPWD",
	# 	"CheckSum" : data_dict['CHECKSUMHASH']
	# }

	dict_string = json.dumps(data_dict)

	print dict_string

	dict_string = urllib.quote_plus(dict_string)
	print "==========================================="
	print dict_string
	print "==========================================="

	# encoded = base64.b64encode(dict_string)

	url = "https://pguat.paytm.com/oltp/HANDLER_FF/withdrawScw?JsonData="+dict_string
	# url = "https://pguat.paytm.com/oltp/HANDLER_FF/withdrawScw/"

	print url

	response = requests.request("POST", url, data = dict_string)

	response = response.json()

	print response
	if 'Error' in response.iterkeys():
		response['status'] = "FAILURE"

	return JsonResponse({'status': response['Status']})

@csrf_exempt
def doTransfer(request):
	if request.method != "POST":
		return JsonResponse({'status': 'FAILURE'})
	data = urlparse.parse_qs(urllib.unquote(urllib.unquote(request.body)))
	print data
	# data = json.dumps(data)
	phone = data['phone'][0]
	email = data['email'][0]
	promoCode = data['promoCode'][0].upper()	
	print phone, promoCode, email

	try:
		p = get_object_or_404(Promos, promoCode=promoCode)
		print p
		if not p.active:
			return JsonResponse({'status': "INACTIVE"})
		url = "http://trust-uat.paytm.in/wallet-web/salesToUserCredit/"
		data = {
			"request": {
					"requestType": "null",
					"merchantGuid": "65ca3267-60d8-4601-8f0f-4bcde3234548",
					"merchantOrderId": str(uuid.uuid4().fields[-1])[:9],
					"salesWalletGuid": "c4e48742-26e2-4f5e-95f2-f5f9bd60f6f7",
					"payeePhoneNumber": phone,
					"appliedToNewUsers": "N",
					"amount": str(p.amount),
					"currencyCode": "INR"
				},
				"metadata": "Let's Pay",
				"ipAddress": "0.0.0.0",
				"platformName": "PayTM",
				"operationType": "SALES_TO_USER_CREDIT"
			}

		checksumHash = generate_checksum_by_str(__get_param_string__(data), "1%!zTZsyiYcgKccf")
		print checksumHash
		headers = {
			"Content-Type": "application/json",
			"MID": "65ca3267-60d8-4601-8f0f-4bcde3234548",
			"Checksumhash": checksumHash
		}
		print "======================"
		print "data :::: \n" , data
		print "======================"
		print "headers :::: \n" , headers
		print "======================"
		print url
		print "======================"
		response = requests.request("POST", url, data=data, headers=headers)
		response = response.json()
		print response
		if(response['status'] != None):
			p.amount=0
			p.active=False
			p.save()
			print "Promo Code", promoCode, "deactivated."
			return JsonResponse({'status': 'SUCCESS'})
	except Promos.DoesNotExist:
		return JsonResponse({'status': 'Promo Code does not Exist.'})
	return JsonResponse({'status': 'FAILURE'})
