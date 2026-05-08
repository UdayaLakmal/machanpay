# Copyright (c) 2026, Lakmal and Contributors
# See license.txt

# import frappe
import frappe
from frappe.tests import IntegrationTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]

from frappe.tests.utils import FrappeTestCase

class IntegrationTestExpense(IntegrationTestCase):
	"""
	Integration tests for Expense.
	Use this class for testing interactions between multiple components.
	"""

	pass

class TestExpense(FrappeTestCase):
	def test_equal_split(self):
		# TODO create test users 
		# To run this test
		# bench --site dreamlink.localhost run-tests --module machanpay.machan_pay.doctype.expense.test_expense --test test_equal_split

		test_expense = frappe.get_doc({
			"doctype": "Expense",
			"date": "2024-01-01",
			"paid_by": "emily.demo@example.com",
			"currency": "USD",
			"description": "Test Expense",
			"amount": 100,
			"split_method": "Equally",
			"splits": [
				{"user": "john.demo@example.com", "currency": "USD"},
				{"user": "friend1@test.com", "currency": "USD"},
			]
		}).insert()

		self.assertEqual(len(test_expense.splits), 2)
		self.assertEqual(test_expense.splits[0].amount, 50)
		self.assertEqual(test_expense.splits[1].amount, 50)



