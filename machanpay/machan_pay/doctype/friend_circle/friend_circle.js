// Copyright (c) 2026, Lakmal and contributors
// For license information, please see license.txt

frappe.ui.form.on("Friend Circle", {
	validate(frm) {
		const owner_user = frm.doc.user;
		const seen_friends = new Set();

		for (const row of frm.doc.friends || []) {
			if (!row.friend) {
				continue;
			}

			if (owner_user && row.friend === owner_user) {
				frappe.throw(__("User cannot be added as their own friend in row {0}.", [row.idx]));
			}

			if (seen_friends.has(row.friend)) {
				frappe.throw(__("Duplicate friend {0} found in row {1}.", [row.friend, row.idx]));
			}

			seen_friends.add(row.friend);
		}
	},
});

frappe.ui.form.on("User Friend", {
	friend(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.friend) {
			return;
		}

		if (frm.doc.user && row.friend === frm.doc.user) {
			frappe.msgprint(__("User cannot be added as their own friend."));
			frappe.model.set_value(cdt, cdn, "friend", null);
			return;
		}

		const is_duplicate = (frm.doc.friends || []).some(
			(item) => item.name !== row.name && item.friend === row.friend
		);

		if (is_duplicate) {
			frappe.msgprint(__("This friend is already added."));
			frappe.model.set_value(cdt, cdn, "friend", null);
		}
	},
});