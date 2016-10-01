from __future__ import unicode_literals

from django.db import models


GENDER = (
	('M', 'Male'),
	('F', 'Female'),
	)


class Merchant(models.Model):
	merchant_id = models.CharField(max_length=30, unique=True, blank=False)
	code = models.CharField(max_length=10)
	name = models.CharField(max_length=50)
	email = models.EmailField()
	phone = models.CharField(max_length=10)

	def __str__(self):
		return "%s" % self.merchant_id

class Expense(models.Model):
	expense_id = models.CharField(max_length=30, unique=True, blank=False)
	description = models.CharField(max_length=100)
	amount = models.FloatField()
	timestamp = models.DateTimeField(auto_now_add=True)
	merchant_id = models.ForeignKey('Merchant')
	user_id = models.ForeignKey('User')

	def __str__(self):
		return "%s" % self.expense_id

class Approval(models.Model):
	approval_id = models.CharField(max_length=30, unique=True, blank=False)
	amount = models.FloatField()
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	master = models.ForeignKey('User',related_name="approval_master", blank=False)
	child = models.ForeignKey('User')

	def __str__(self):
		return "%s" % self.approval_id

class User(models.Model):
	user_id = models.CharField(max_length=30, unique=True, blank=False)
	name = models.CharField(max_length=50, blank=False)
	phone = models.CharField(max_length=10, blank=False)
	email = models.EmailField()
	gender = models.CharField(max_length=1, choices=GENDER, default='M')
	allowance = models.IntegerField()
	is_master = models.BooleanField(default=False)
	is_child = models.BooleanField(default=False)
	master = models.ForeignKey('User', related_name="user_master", blank=True, null=True)

	def __str__(self):
		return "%s" % self.user_id

