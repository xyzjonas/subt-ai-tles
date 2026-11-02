<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useMembershipRequests } from "../../composables/useMembershipRequests";
import type { MembershipRequestStatus } from "../../api/types";
import SegmentedTabs from "../ui/SegmentedTabs.vue";
import MembershipRequestItem from "./MembershipRequestItem.vue";

const { t } = useI18n();
const { status, requests, loading, error, approve, reject, drop } = useMembershipRequests();

const STATUSES: MembershipRequestStatus[] = ["pending", "approved", "rejected"];
const tabs = computed(() => STATUSES.map((value) => ({ value, label: t(`membership.admin.status.${value}`) })));
</script>

<template>
  <div class="requests">
    <p class="intro">{{ t("membership.admin.intro") }}</p>
    <SegmentedTabs v-model="status" :tabs="tabs" :label="t('membership.admin.filter')" />

    <p v-if="loading" class="status" role="status">{{ t("loading") }}</p>
    <p v-else-if="error" class="status" role="alert">{{ error }}</p>
    <p v-else-if="!requests.length" class="status" role="status">{{ t(`membership.admin.empty.${status}`) }}</p>
    <ul v-else class="list">
      <li v-for="r in requests" :key="r.id">
        <MembershipRequestItem :request="r" :approve="approve" :reject="reject" @decided="drop" />
      </li>
    </ul>
  </div>
</template>

<style scoped>
.requests {
  display: grid;
  gap: 16px;
}

.intro {
  font-size: 13px;
  color: var(--text-secondary);
}

.status {
  padding: 32px 0;
  text-align: center;
  color: var(--text-muted);
}

.list {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}
</style>
