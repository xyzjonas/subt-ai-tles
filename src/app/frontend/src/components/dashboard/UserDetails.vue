<script setup lang="ts">
import type { CurrentUser } from "../../api/types";
import { formatCredits } from "../../utils/usage";
import { formatWhen } from "../../utils/srt";

defineProps<{ user: CurrentUser }>();
</script>

<template>
  <section class="details" aria-labelledby="details-title">
    <h2 id="details-title">Account</h2>
    <dl>
      <div>
        <dt>Username</dt>
        <dd>{{ user.username }}</dd>
      </div>
      <div>
        <dt>Role</dt>
        <dd>{{ user.isAdmin ? "Administrator" : "Member" }}</dd>
      </div>
      <div>
        <dt>Monthly quota</dt>
        <dd><span class="mono">{{ formatCredits(user.monthlyQuota) }}</span> credits</dd>
      </div>
      <div>
        <dt>Member since</dt>
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
