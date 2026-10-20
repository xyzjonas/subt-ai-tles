<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { CurrentUser } from "../../api/types";
import { LOCALE_FLAGS } from "../../utils/language";
import { formatCredits } from "../../utils/usage";

defineProps<{ users: CurrentUser[]; currentId?: number }>();
defineEmits<{ select: [id: number] }>();

const { t } = useI18n();
</script>

<template>
  <ul class="users">
    <li v-for="u in users" :key="u.id">
      <button type="button" class="row" @click="$emit('select', u.id)">
        <span class="who">
          <strong>{{ u.username }}</strong>
          <span v-if="u.locale" class="flag" role="img" :aria-label="t('locale.flag', { name: t(`locale.names.${u.locale}`) })" :title="t('locale.flag', { name: t(`locale.names.${u.locale}`) })">{{ LOCALE_FLAGS[u.locale] }}</span>
          <span v-if="u.id === currentId" class="tag">{{ t("users.you") }}</span>
          <span v-if="u.isAdmin" class="tag admin">{{ t("users.admin") }}</span>
          <span v-if="!u.isActive" class="tag blocked">{{ t("users.blocked") }}</span>
          <span v-else-if="u.mustChangePassword" class="tag pending">{{ t("users.temporaryPassword") }}</span>
        </span>
        <span class="quota mono">{{ t("users.quotaPerMonth", { amount: formatCredits(u.monthlyQuota) }) }}</span>
      </button>
    </li>
  </ul>
</template>

<style scoped>
.users {
  display: grid;
  margin: 0;
  padding: 0;
  list-style: none;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

li + li {
  border-top: 1px solid var(--border-soft);
}

.row {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 6px 12px;
  width: 100%;
  padding: 14px 16px;
  border: 0;
  background: none;
  font: inherit;
  text-align: left;
  color: inherit;
  cursor: pointer;
}

.row:hover {
  background: var(--surface-subdued);
}

.who {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.flag {
  font-size: 14px;
  line-height: 1;
}

.quota {
  font-size: 13px;
  color: var(--text-secondary);
}

.tag {
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--surface-subdued);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
}

.tag.admin {
  background: var(--primary-tint);
  color: var(--primary);
}

.tag.pending {
  background: var(--warning-bg);
  color: var(--warning-strong);
}

.tag.blocked {
  background: var(--danger-bg);
  color: var(--danger);
}
</style>
