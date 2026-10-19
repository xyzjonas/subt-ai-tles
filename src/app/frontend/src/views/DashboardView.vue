<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import SegmentedTabs from "../components/ui/SegmentedTabs.vue";
import SettingsTab from "../components/dashboard/SettingsTab.vue";
import UsageTab from "../components/dashboard/UsageTab.vue";
import UserDetails from "../components/dashboard/UserDetails.vue";
import { useCurrentUser } from "../composables/useCurrentUser";

type DashboardTab = "details" | "usage" | "settings";

const tab = ref<DashboardTab>("details");
const { user, load } = useCurrentUser();
onMounted(load);

/** Settings is for admins only; the backend enforces it too. */
const tabs = computed<{ value: DashboardTab; label: string }[]>(() => [
  { value: "details", label: "User details" },
  { value: "usage", label: "Usage" },
  ...(user.value?.isAdmin ? [{ value: "settings" as const, label: "Settings" }] : []),
]);
</script>

<template>
  <section class="dashboard">
    <header class="head">
      <h1>Dashboard</h1>
      <p>Your account and what your translations cost.</p>
    </header>

    <SegmentedTabs v-model="tab" :tabs="tabs" label="Dashboard sections" />

    <template v-if="tab === 'details'">
      <UserDetails v-if="user" :user="user" />
      <p v-else class="empty" role="status">Loading…</p>
    </template>
    <UsageTab v-else-if="tab === 'usage'" />
    <SettingsTab v-else-if="user?.isAdmin" />
  </section>
</template>

<style scoped>
.dashboard {
  display: grid;
  gap: 16px;
}

.head {
  display: grid;
  gap: 4px;
}

h1 {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.head p {
  font-size: 13px;
  color: var(--text-secondary);
}

.empty {
  padding: 32px 0;
  text-align: center;
  color: var(--text-muted);
}
</style>
