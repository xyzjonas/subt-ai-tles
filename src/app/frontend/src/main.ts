import { createApp, watch } from "vue";
import App from "./App.vue";
import { setUnauthorizedHandler } from "./api/http";
import { i18n } from "./i18n";
import { router, updateDocumentTitle } from "./router";
import "./styles/base.css";

// A 401 mid-session (expired or revoked credentials): sign in again, then come back here.
setUnauthorizedHandler(() => {
  const { name, fullPath } = router.currentRoute.value;
  if (name !== "login") router.replace({ name: "login", query: { redirect: fullPath } });
});

// Route titles are translation keys, so the tab title follows the language.
watch(i18n.global.locale, updateDocumentTitle);

createApp(App).use(router).use(i18n).mount("#app");
