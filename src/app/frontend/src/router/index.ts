import { createRouter, createWebHistory } from "vue-router";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "translate", component: () => import("../views/TranslateView.vue"), meta: { title: "Translate .SRT", subtitle: "Translate" } },
    { path: "/requests", name: "requests", component: () => import("../views/PlaceholderView.vue"), meta: { title: "My Requests", subtitle: "My Requests" } },
    { path: "/jobs/:id", name: "job", component: () => import("../views/PlaceholderView.vue"), meta: { title: "Translating", subtitle: "Translating" } },
  ],
});

router.afterEach((to) => {
  document.title = `${to.meta.title} - subt-ai-tles`;
});
