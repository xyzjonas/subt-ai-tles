<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import type { CurrentUser, MembershipRequest } from "../../api/types";
import ApproveRequestForm from "./ApproveRequestForm.vue";

const { t, locale } = useI18n();
const props = defineProps<{
  request: MembershipRequest;
  approve: (id: number, password: string) => Promise<{ user?: CurrentUser; failure: string }>;
  reject: (id: number) => Promise<string>;
}>();
const emit = defineEmits<{ decided: [id: number] }>();

const approving = ref(false);
const rejecting = ref(false);
const error = ref("");

async function rejectRequest() {
  rejecting.value = true;
  error.value = await props.reject(props.request.id);
  rejecting.value = false;
}
</script>

<template>
  <article class="item">
    <header>
      <h3>{{ request.email }}</h3>
      <time :datetime="request.createdAt">{{ t("membership.admin.received", { date: new Date(request.createdAt).toLocaleDateString(locale, { dateStyle: "medium" }) }) }}</time>
    </header>
    <p class="details" :class="{ none: !request.details }">{{ request.details ?? t("membership.admin.noDetails") }}</p>

    <template v-if="request.status === 'pending'">
      <ApproveRequestForm v-if="approving" :email="request.email" :approve="(password) => approve(request.id, password)" @cancel="approving = false" @done="emit('decided', request.id)" />
      <div v-else class="actions">
        <button type="button" class="action-reject" :disabled="rejecting" @click="rejectRequest">{{ rejecting ? t("membership.admin.rejecting") : t("membership.admin.reject") }}</button>
        <button type="button" class="action-approve" @click="approving = true">{{ t("membership.admin.approve") }}</button>
      </div>
      <p v-if="error" class="fail" role="alert">{{ error }}</p>
    </template>
  </article>
</template>

<style scoped>
.item {
  display: grid;
  gap: 10px;
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 4px 12px;
}

h3 {
  font-size: 15px;
  font-weight: 600;
  overflow-wrap: anywhere;
}

time {
  font-size: 12px;
  color: var(--text-muted);
}

.details {
  font-size: 14px;
  white-space: pre-line;
  overflow-wrap: anywhere;
}

.details.none {
  color: var(--text-muted);
}

.actions {
  display: flex;
  gap: 10px;
}

button {
  height: 40px;
  padding: 0 18px;
  border-radius: var(--radius-md);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-approve {
  flex: 1;
  border: 0;
  background: var(--primary);
  box-shadow: var(--shadow-primary);
  color: #fff;
}

.action-approve:hover {
  background: var(--primary-hover);
}

.action-reject {
  border: 1px solid #fecaca;
  background: #fee2e2;
  color: #dc2626;
}

.fail {
  font-size: 13px;
  color: var(--danger);
}
</style>
