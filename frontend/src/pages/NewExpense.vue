<template>
	<div class="new-expense-page">
		<div class="new-expense-card">
			<header class="top-row">
				<h1>New Expense</h1>
				<Button :loading="saveExpense.loading" :disabled="saveExpense.loading" @click="submitExpense">Save</Button>
			</header>

			<div class="form-grid">
				<FormControl label="Description">
					<TextInput v-model="form.description" placeholder="Ice cream" />
				</FormControl>

				<FormControl label="Amount">
					<TextInput v-model="form.amount" type="number" min="0" step="0.01" placeholder="1200" />
				</FormControl>

				<FormControl label="Expense Date">
					<TextInput v-model="form.date" type="date" />
				</FormControl>
			</div>

			<div class="split-row">
				<p>
					Paid by
					<select v-model="form.paid_by" class="select-input">
						<option v-for="u in paidByOptions" :key="u" :value="u">
							{{ displayUser(u) }}
						</option>
					</select>
					and split
					<select v-model="form.split_method" class="select-input">
						<option value="Equally">Equally</option>
						<option value="Manual">Manual</option>
					</select>
				</p>
			</div>

			<section>
				<p class="section-title">Split with</p>
				<div class="split-users">
					<span v-for="u in splitUsers" :key="u" class="chip">{{ displayUser(u) }}</span>
				</div>
			</section>

			<section>
				<p class="section-title">Add new user</p>
				<div class="add-user-row">
					<TextInput v-model="newUser" placeholder="user@example.com" @keydown.enter.prevent="addUser" />
					<Button variant="outline" @click="addUser">Add</Button>
				</div>
			</section>

			<ErrorMessage v-if="errorMessage" :message="errorMessage" />
		</div>
	</div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { createResource } from "frappe-ui"

import { session } from "@/data/session"
import { userResource } from "@/data/user"

const router = useRouter()

const currentUser = computed(() => session.user || userResource.data || "")

const form = reactive({
	description: "",
	amount: "",
	date: new Date().toISOString().slice(0, 10),
	paid_by: "",
	split_method: "Equally",
})

const splitUsers = ref([])
const newUser = ref("")
const errorMessage = ref("")
const friendCircleName = ref("")

const loadFriendCircle = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Friend Circle",
			fields: ["name", "user"],
			filters: { user: currentUser.value || "" },
			limit_page_length: 1,
		}
	},
	onSuccess(data) {
		friendCircleName.value = data?.[0]?.name || ""
		if (friendCircleName.value) {
			loadFriendUsers.submit(friendCircleName.value)
		} else if (currentUser.value) {
			splitUsers.value = [currentUser.value]
			form.paid_by = currentUser.value
		}
	},
})

function initializeSplitUsers() {
	if (!currentUser.value) return
	loadFriendCircle.submit()
}

onMounted(() => {
	initializeSplitUsers()
})

watch(currentUser, (value) => {
	if (value && !splitUsers.value.length) {
		initializeSplitUsers()
	}
})

const loadFriendUsers = createResource({
	url: "frappe.client.get_list",
	makeParams(circleName) {
		return {
			doctype: "User Friend",
			fields: ["friend"],
			filters: {
				parent: circleName,
				parenttype: "Friend Circle",
				parentfield: "friends",
			},
			order_by: "creation asc",
			limit_page_length: 200,
		}
	},
	onSuccess(rows) {
		const users = rows.map((row) => row.friend).filter(Boolean)
		const set = new Set([currentUser.value, ...users].filter(Boolean))
		splitUsers.value = [...set]
		if (!form.paid_by) {
			form.paid_by = currentUser.value || splitUsers.value[0] || ""
		}
	},
	onError(error) {
		errorMessage.value = error?.messages?.[0] || error?.message || "Failed to load friend users"
	},
})

const createFriendCircle = createResource({
	url: "frappe.client.insert",
	makeParams(user) {
		return {
			doc: {
				doctype: "Friend Circle",
				user,
			},
		}
	},
	onSuccess(doc) {
		friendCircleName.value = doc.name
	},
})

const addFriendToCircle = createResource({
	url: "frappe.client.insert",
	makeParams({ circleName, friend }) {
		return {
			doc: {
				doctype: "User Friend",
				parenttype: "Friend Circle",
				parentfield: "friends",
				parent: circleName,
				friend,
			},
		}
	},
})

const saveExpense = createResource({
	url: "frappe.client.insert",
	makeParams(payload) {
		return {
			doc: {
				doctype: "Expense",
				paid_by: payload.paid_by,
				split_method: payload.split_method,
				date: payload.date,
				amount: payload.amount,
				description: payload.description,
				currency: "LKR",
				splits: payload.splits,
			},
		}
	},
	onSuccess() {
		router.push({ name: "Dashboard" })
	},
	onError(error) {
		errorMessage.value = error?.messages?.[0] || error?.message || "Failed to save expense"
	},
})

const paidByOptions = computed(() => {
	if (!splitUsers.value.length && currentUser.value) {
		return [currentUser.value]
	}
	return splitUsers.value
})

function displayUser(user) {
	if (!user) return "-"
	return user === currentUser.value ? "You" : user
}

async function ensureFriendCircleExists() {
	if (friendCircleName.value) return friendCircleName.value
	if (!currentUser.value) return ""
	const result = await createFriendCircle.submit(currentUser.value)
	friendCircleName.value = result?.name || friendCircleName.value
	return friendCircleName.value
}

async function addUser() {
	errorMessage.value = ""
	const candidate = newUser.value.trim()
	if (!candidate) return
	if (splitUsers.value.includes(candidate)) {
		newUser.value = ""
		return
	}

	try {
		const circleName = await ensureFriendCircleExists()
		if (circleName) {
			await addFriendToCircle.submit({
				circleName,
				friend: candidate,
			})
		}
		splitUsers.value = [...splitUsers.value, candidate]
		newUser.value = ""
	} catch (error) {
		errorMessage.value = error?.messages?.[0] || error?.message || "Could not add user"
	}
}

function splitAmount(amount, users, splitMethod) {
	if (!users.length) return []
	if (splitMethod === "Manual") {
		return users.map((user) => ({ user, amount: 0, currency: "LKR" }))
	}
	const perUser = Number(amount) / users.length
	return users.map((user) => ({ user, amount: perUser, currency: "LKR" }))
}

function validateForm() {
	if (!form.description.trim()) return "Description is required"
	if (!Number(form.amount)) return "Amount must be greater than zero"
	if (!form.date) return "Date is required"
	if (!form.paid_by) return "Paid by is required"
	if (!splitUsers.value.length) return "At least one split user is required"
	return ""
}

async function submitExpense() {
	errorMessage.value = ""
	const validationError = validateForm()
	if (validationError) {
		errorMessage.value = validationError
		return
	}

	const payload = {
		description: form.description.trim(),
		amount: Number(form.amount),
		date: form.date,
		paid_by: form.paid_by,
		split_method: form.split_method,
		splits: splitAmount(Number(form.amount), splitUsers.value, form.split_method),
	}
	await saveExpense.submit(payload)
}
</script>

<style scoped>
.new-expense-page {
	min-height: 100vh;
	padding: 2rem 1rem;
	background: radial-gradient(circle at 20% 20%, #f4f6fb 0%, #ece8df 45%, #e0ebf0 100%);
}

.new-expense-card {
	max-width: 760px;
	margin: 0 auto;
	padding: 1.25rem;
	background: #fffffff7;
	border: 1px solid #d4d7de;
	border-radius: 16px;
	box-shadow: 0 10px 25px rgba(23, 36, 55, 0.08);
	display: grid;
	gap: 1rem;
}

.top-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 1rem;
}

h1 {
	margin: 0;
	font-size: 1.9rem;
}

.form-grid {
	display: grid;
	gap: 0.75rem;
}

.split-row p {
	margin: 0;
	font-size: 1.1rem;
	font-weight: 600;
	display: flex;
	align-items: center;
	gap: 0.5rem;
	flex-wrap: wrap;
}

.select-input {
	padding: 0.35rem 0.5rem;
	border-radius: 9px;
	border: 1px solid #c8ced8;
	background: #f8fafc;
}

.section-title {
	margin: 0 0 0.45rem;
	font-weight: 600;
	color: #334155;
}

.split-users {
	display: flex;
	flex-wrap: wrap;
	gap: 0.5rem;
}

.chip {
	padding: 0.35rem 0.6rem;
	border: 1px solid #c9d5e6;
	border-radius: 999px;
	font-size: 0.92rem;
	background: #eff6ff;
	color: #1e3a5f;
}

.add-user-row {
	display: grid;
	grid-template-columns: 1fr auto;
	gap: 0.6rem;
	align-items: center;
}

@media (max-width: 640px) {
	.top-row {
		align-items: flex-start;
		flex-direction: column;
	}

	.add-user-row {
		grid-template-columns: 1fr;
	}
}
 </style>
