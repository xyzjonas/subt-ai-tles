<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { CurrentUser } from "../../api/types";
import LocaleSetting from "./LocaleSetting.vue";
import { formatCredits } from "../../utils/usage";
import { formatWhen } from "../../utils/srt";

defineProps<{ user: CurrentUser }>();

const { t } = useI18n();
</script>

<template>
  <section class="details" aria-labelledby="details-title">
    <h2 id="details-title">{{ t("dashboard.details.title") }}</h2>
    <dl>
      <div>
        <dt>{{ t("dashboard.details.username") }}</dt>
        <dd>{{ user.username }}</dd>
      </div>
      <div>
        <dt>{{ t("dashboard.details.role") }}</dt>
        <dd>{{ user.isAdmin ? t("dashboard.details.admin") : t("dashboard.details.member") }}</dd>
      </div>
      <div>
        <dt>{{ t("dashboard.details.quota") }}</dt>
        <dd class="mono">{{ t("dashboard.credits", { amount: formatCredits(user.monthlyQuota) }, user.monthlyQuota) }}</dd>
      </div>
      <div>
        <dt><label for="ui-language">{{ t("locale.setting") }}</label></dt>
        <dd><LocaleSetting /></dd>
      </div>
      <div>
        <dt>{{ t("dashboard.details.since") }}</dt>
        <dd>
          <time :datetime="user.createdAt">{{ formatWhen(user.createdAt) }}</time>
        </dd>
      </div>
    </dl>
  </section>
</template>

<style scoped>
.details {
  display: grid;
  gap: 12px;
}

h2 {
  font-size: 16px;
  font-weight: 600;
}

dl {
  display: grid;
  margin: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

dl div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-soft);
}

dl div:last-child {
  border-bottom: 0;
}

dt {
  color: var(--text-secondary);
}

dd {
  margin: 0;
  font-weight: 600;
}
</style>
