from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Promos(models.Model):
	user = models.ForeignKey('PayUser', null=True)
	promoCode = models.CharField(max_length=20, blank=False, null=False)
	amount = models.FloatField(blank=False, null=True)
	email = models.EmailField()
	phone = models.CharField(max_length=10,  blank=False, null=False)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return "%s" % self.promoCode

class PayUser(models.Model):
	user = models.ForeignKey(User, blank=False, null=True)
	password = models.CharField(max_length=30, blank=False, null=True, error_messages={'required': 'This field is required'})
	name = models.CharField(max_length=50, blank=False)
	phone = models.CharField(max_length=10, blank=False, null=False)
	email = models.EmailField()

	def __str__(self):
		return str(self.user)

