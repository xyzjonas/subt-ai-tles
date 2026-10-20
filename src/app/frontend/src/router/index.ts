import { createRouter, createWebHistory } from "vue-router";
import { ApiError } from "../api/http";
import { isSignedIn } from "../api/session";
import { t } from "../i18n";
import { useCurrentUser } from "../composables/useCurrentUser";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: () => import("../views/LoginView.vue"), meta: { title: "routes.login", public: true, layout: "bare" } },
    { path: "/change-password", name: "change-password", component: () => import("../views/ChangePasswordView.vue"), meta: { title: "routes.changePassword", layout: "bare" } },
    { path: "/", name: "translate", component: () => import("../views/TranslateView.vue"), meta: { title: "routes.translate", subtitle: "nav.translate" } },
    { path: "/requests", name: "requests", component: () => import("../views/RequestsView.vue"), meta: { title: "routes.requests", subtitle: "nav.requests" } },
    { path: "/dashboard", name: "dashboard", component: () => import("../views/DashboardView.vue"), meta: { title: "routes.dashboard", subtitle: "nav.dashboard" } },
    { path: "/jobs/:id/edit", name: "editor", component: () => import("../views/EditorView.vue"), meta: { title: "routes.editor", subtitle: "routes.editorSubtitle", layout: "stack" } },
    { path: "/jobs/:id", name: "job", component: () => import("../views/ProgressView.vue"), meta: { title: "routes.job", subtitle: "routes.editorSubtitle", layout: "stack" } },
  ],
});

router.beforeEach(async (to) => {
  if (to.meta.public) return isSignedIn() && to.name === "login" ? { path: "/" } : true;
  if (!isSignedIn()) return { name: "login", query: { redirect: to.fullPath } };

  // A temporary password has to be replaced before anything else works.
  const { user, load } = useCurrentUser();
  try {
    await load();
  } catch (e) {
    return e instanceof ApiError && e.status === 401 ? { name: "login", query: { redirect: to.fullPath } } : true;
  }
  const pending = user.value?.mustChangePassword ?? false;
  if (pending && to.name !== "change-password") return { name: "change-password" };
  return pending || to.name !== "change-password" ? true : { path: "/" };
});

export function updateDocumentTitle() {
  document.title = `${t(String(router.currentRoute.value.meta.title))} - subt-ai-tles`;
}

router.afterEach(updateDocumentTitle);
