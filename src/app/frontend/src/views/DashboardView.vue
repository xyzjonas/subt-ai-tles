<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import SegmentedTabs from "../components/ui/SegmentedTabs.vue";
import SettingsTab from "../components/dashboard/SettingsTab.vue";
import UsersTab from "../components/users/UsersTab.vue";
import UsageTab from "../components/dashboard/UsageTab.vue";
import UserDetails from "../components/dashboard/UserDetails.vue";
import { useCurrentUser } from "../composables/useCurrentUser";

type DashboardTab = "details" | "usage" | "users" | "settings";

const { t } = useI18n();
const tab = ref<DashboardTab>("details");
const { user, load } = useCurrentUser();
onMounted(load);

/** Users and Settings are for admins only; the backend enforces it too. */
const tabs = computed<{ value: DashboardTab; label: string }[]>(() => [
  { value: "details", label: t("dashboard.tabs.details") },
  { value: "usage", label: t("dashboard.tabs.usage") },
  ...(user.value?.isAdmin
    ? [
        { value: "users" as const, label: t("dashboard.tabs.users") },
        { value: "settings" as const, label: t("dashboard.tabs.settings") },
      ]
    : []),
]);
</script>

<template>
  <section class="dashboard">
    <header class="head">
      <h1>{{ t("dashboard.title") }}</h1>
      <p>{{ t("dashboard.lead") }}</p>
    </header>

    <SegmentedTabs v-model="tab" :tabs="tabs" :label="t('dashboard.sections')" />

    <template v-if="tab === 'details'">
      <UserDetails v-if="user" :user="user" />
      <p v-else class="empty" role="status">{{ t("loading") }}</p>
    </template>
    <UsageTab v-else-if="tab === 'usage'" />
    <UsersTab v-else-if="tab === 'users' && user?.isAdmin" />
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
