# Copyright (c) 2026, Lakmal and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class Expense(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from machanpay.machan_pay.doctype.expense_split.expense_split import ExpenseSplit

		amended_from: DF.Link | None
		amount: DF.Currency
		currency: DF.Link
		date: DF.Date
		description: DF.Data
		name: DF.Int | None
		notes: DF.SmallText | None
		paid_by: DF.Link
		split_method: DF.Literal["Equally", "Manual"]
		splits: DF.Table[ExpenseSplit]
	# end: auto-generated types

	def before_save(self):
		self.apply_split_method()

	def apply_split_method(self):
		if self.split_method == "Equally":
			# For equal split, divide the amount by the number of splits
			self.calculate_equal_splits()
		else:
			# For manual split, ensure that the total of splits equals the amount
			total_split_amount = sum(split.amount for split in self.splits)
			if total_split_amount != self.amount:
				frappe.throw("Total of splits must equal the total amount for manual split method.")
				

	def calculate_equal_splits(self):
		num_splits = len(self.splits)
		split = self.amount / num_splits if num_splits > 0 else 0
		for split_entry in self.splits:
			split_entry.amount = split
	