import { createApp } from "vue";
import App from "./App.vue";
import { setUnauthorizedHandler } from "./api/http";
import { router } from "./router";
import "./styles/base.css";

// A 401 mid-session (expired or revoked credentials): sign in again, then come back here.
setUnauthorizedHandler(() => {
  const { name, fullPath } = router.currentRoute.value;
  if (name !== "login") router.replace({ name: "login", query: { redirect: fullPath } });
});

createApp(App).use(router).mount("#app");
