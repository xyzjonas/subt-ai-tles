<script setup lang="ts">
import { useRouter } from "vue-router";
import { clearSession } from "../../api/session";
import AppIcon from "../ui/AppIcon.vue";
import StatusBadge from "../ui/StatusBadge.vue";

defineProps<{ subtitle: string }>();

const router = useRouter();

function signOut() {
  clearSession();
  router.push({ name: "login" });
}
</script>

<template>
  <header class="header">
    <div class="bar">
      <RouterLink to="/" class="brand">
        <span class="emblem"><AppIcon name="translate" :size="18" /></span>
        <span>
          <strong>subt-ai-tles</strong>
          <small>{{ subtitle }}</small>
        </span>
      </RouterLink>
      <nav class="nav" aria-label="Primary">
        <RouterLink to="/">Translate</RouterLink>
        <RouterLink to="/requests">My requests</RouterLink>
      </nav>
      <StatusBadge tone="success" dot pulse>LLM v2.4 Active</StatusBadge>
      <button type="button" class="avatar" aria-label="Sign out" title="Sign out" @click="signOut">
        <AppIcon name="user" :size="18" />
      </button>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: fixed;
  inset: 0 0 auto;
  z-index: 10;
  height: var(--header-height);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}

.bar {
  max-width: var(--content-max);
  height: 100%;
  margin: 0 auto;
  padding: 0 var(--page-padding);
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: auto;
}

.brand span:last-child {
  display: grid;
  line-height: 1.15;
}

strong {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

small {
  font-size: 11px;
  color: var(--text-muted);
}

.emblem {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #fff;
}

.avatar {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 50%;
  background: var(--surface-subdued);
  color: var(--text-secondary);
}

.avatar:hover {
  background: var(--border);
}

.nav {
  display: none;
}

@media (min-width: 768px) {
  .nav {
    display: flex;
    gap: 4px;
    margin-right: 8px;
  }

  .nav a {
    padding: 8px 14px;
    border-radius: var(--radius-sm);
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .nav a:hover {
    background: var(--surface-subdued);
  }

  .nav a.router-link-exact-active {
    background: var(--primary-tint);
    color: var(--primary);
  }
}

@media (max-width: 380px) {
  .bar :deep(.badge) {
    display: none;
  }
}
</style>
