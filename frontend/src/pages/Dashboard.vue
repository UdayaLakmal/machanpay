<template>
  <div class="dashboard-page">
    <div class="dashboard-card">
      <header class="header-row">
        <div>
          <h1>Dashboard</h1>
          <p class="subtext">Overall, total expenses: {{ currency }} {{ totalExpense.toFixed(2) }}</p>
        </div>
        <Button variant="solid" @click="goToNewExpense">Add expense</Button>
      </header>

      <div v-if="expenseResource.list.loading" class="state-text">Loading expenses...</div>
      <div v-else-if="!expenses.length" class="state-text">No expenses yet. Add your first expense.</div>

      <ul v-else class="expense-list">
        <li v-for="expense in expenses" :key="expense.name" class="expense-item">
          <div>
            <p class="expense-title">{{ expense.description }}</p>
            <p class="expense-meta">
              {{ formatDate(expense.date) }}
              · Paid by {{ displayUser(expense.paid_by) }}
              · Split {{ expense.split_method }}
            </p>
          </div>
          <p class="expense-amount">{{ expense.currency || currency }} {{ Number(expense.amount || 0).toFixed(2) }}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { createListResource } from "frappe-ui"

import { session } from "@/data/session"
import { userResource } from "@/data/user"

const router = useRouter()

const expenseResource = createListResource({
  doctype: "Expense",
  fields: ["name", "description", "amount", "currency", "date", "paid_by", "split_method"],
  orderBy: "creation desc",
  pageLength: 100,
  auto: true,
})

const currentUser = computed(() => session.user || userResource.data || "")
const expenses = computed(() => expenseResource.data || [])
const currency = computed(() => expenses.value[0]?.currency || "LKR")

const totalExpense = computed(() => {
  return expenses.value.reduce((total, expense) => {
    return total + Number(expense.amount || 0)
  }, 0)
})

function displayUser(user) {
  if (!user) return "-"
  return user === currentUser.value ? "You" : user
}

function formatDate(value) {
  if (!value) return "-"
  return new Date(value).toLocaleDateString("en-GB")
}

function goToNewExpense() {
  router.push({ name: "NewExpense" })
}
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  padding: 2rem 1rem;
  background: linear-gradient(140deg, #f7f5f1 0%, #e9ecef 100%);
}

.dashboard-card {
  max-width: 760px;
  margin: 0 auto;
  padding: 1.25rem;
  background: #ffffffee;
  border: 1px solid #d3d5d9;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(18, 28, 45, 0.08);
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

h1 {
  margin: 0;
  font-size: 1.8rem;
  line-height: 1.1;
}

.subtext {
  margin: 0.4rem 0 0;
  color: #4f5968;
  font-size: 0.95rem;
}

.state-text {
  padding: 2rem 1rem;
  text-align: center;
  color: #4f5968;
}

.expense-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.75rem;
}

.expense-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border: 1px solid #d9dce2;
  border-radius: 12px;
  background: #fff;
}

.expense-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
}

.expense-meta {
  margin: 0.25rem 0 0;
  font-size: 0.9rem;
  color: #647085;
}

.expense-amount {
  margin: 0;
  white-space: nowrap;
  font-weight: 700;
  font-size: 1rem;
  color: #1f2937;
}

@media (max-width: 640px) {
  .header-row,
  .expense-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .dashboard-card {
    padding: 1rem;
  }
}
</style>
