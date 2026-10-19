import { createRouter, createWebHistory } from "vue-router";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "translate", component: () => import("../views/TranslateView.vue"), meta: { title: "Translate .srt", subtitle: "Translate" } },
    { path: "/requests", name: "requests", component: () => import("../views/RequestsView.vue"), meta: { title: "My requests", subtitle: "My requests" } },
    { path: "/jobs/:id/edit", name: "editor", component: () => import("../views/EditorView.vue"), meta: { title: "Export & Format", subtitle: "subt-ai-tles editor", layout: "stack" } },
    { path: "/jobs/:id", name: "job", component: () => import("../views/ProgressView.vue"), meta: { title: "Translating", subtitle: "subt-ai-tles editor", layout: "stack" } },
  ],
});

router.afterEach((to) => {
  document.title = `${to.meta.title} - subt-ai-tles`;
});
