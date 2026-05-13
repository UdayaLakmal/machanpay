import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Dashboard",
		component: () => import("@/pages/Dashboard.vue"),
	},
	{
		path: "/expense/new",
		name: "NewExpense",
		component: () => import("@/pages/NewExpense.vue"),
	},
]

const routerBase = import.meta.env.DEV ? "/" : "/frontend"

const router = createRouter({
	history: createWebHistory(routerBase),
	routes,
})

router.beforeEach(async (to, from, next) => {
	const isLocalViteDev =
		import.meta.env.DEV && ["localhost", "127.0.0.1"].includes(window.location.hostname)

	if (isLocalViteDev) {
		next()
		return
	}

	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
	} catch (error) {
		isLoggedIn = false
	}
	if (!isLoggedIn) {
		window.location.href = "/login?redirect_to=/frontend"
		return
	}
	next()
	// if (to.name === "Login" && isLoggedIn) {
	// 	next({ name: "Home" })
	// } else if (to.name !== "Login" && !isLoggedIn) {
	// 	window.location.href = "/login"
	// } else {
	// 	next()
	// }
})

export default router
