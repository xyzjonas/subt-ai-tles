<script setup lang="ts">
import { ref } from "vue";
import AppIcon from "../ui/AppIcon.vue";

defineProps<{ cancelling: boolean }>();
defineEmits<{ cancel: [] }>();

const notify = ref(false);

async function toggleNotify() {
  if (!notify.value && "Notification" in window && Notification.permission === "default") {
    if ((await Notification.requestPermission()) !== "granted") return;
  }
  notify.value = !notify.value;
}
</script>

<template>
  <section class="controls">
    <div class="notify">
      <AppIcon name="bell" :size="20" />
      <label for="notify" class="text">
        <strong>Notify when complete</strong>
        <small>Send push alert upon compilation</small>
      </label>
      <button id="notify" type="button" role="switch" class="switch" :aria-checked="notify" @click="toggleNotify" />
    </div>

    <button type="button" class="cancel" :disabled="cancelling" @click="$emit('cancel')">
      <AppIcon name="stop" :size="16" /> {{ cancelling ? "Cancelling…" : "Cancel Translation" }}
    </button>
    <p class="foot">Tokens consumed will reflect progress made</p>
  </section>
</template>

<style scoped>
.controls {
  display: grid;
  gap: 12px;
  justify-items: center;
}

.notify {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
}

.text {
  display: grid;
  flex: 1;
  gap: 2px;
}

strong {
  font-size: 14px;
  color: var(--text);
}

small {
  font-size: 12px;
  color: var(--text-muted);
}

.switch {
  position: relative;
  flex: none;
  width: 44px;
  height: 24px;
  border: 0;
  border-radius: 12px;
  background: var(--border);
  cursor: pointer;
  transition: background 0.2s;
}

.switch::after {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.25);
  transition: translate 0.2s;
}

.switch[aria-checked="true"] {
  background: var(--primary);
}

.switch[aria-checked="true"]::after {
  translate: 20px 0;
}

.cancel {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  height: 44px;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  background: #fee2e2;
  color: #991b1b;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.cancel:hover:not(:disabled) {
  background: #fecaca;
}

.cancel:disabled {
  opacity: 0.7;
  cursor: progress;
}

.foot {
  font-size: 11px;
  color: var(--text-muted);
}
</style>
