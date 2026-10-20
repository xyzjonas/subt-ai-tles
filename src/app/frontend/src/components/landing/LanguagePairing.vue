<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { Language } from "../../api/types";
import { languageLabel } from "../../utils/language";
import AppIcon from "../ui/AppIcon.vue";

defineProps<{ languages: Language[] }>();
const targetCode = defineModel<string>("targetCode", { required: true });

const { locale } = useI18n();
</script>

<template>
  <section class="target">
    <label for="target-language" class="section-label">{{ $t("translate.target") }}</label>
    <div class="select">
      <select id="target-language" v-model="targetCode">
        <option v-for="lang in languages" :key="lang.code" :value="lang.code">{{ languageLabel(lang, locale) }}</option>
      </select>
      <AppIcon name="chevron" :size="16" />
    </div>
  </section>
</template>

<style scoped>
.target {
  display: grid;
  gap: 10px;
}

.select {
  position: relative;
  display: grid;
}

select {
  appearance: none;
  width: 100%;
  padding: 14px 40px 14px 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: inherit;
  font: inherit;
  font-size: 15px;
  font-weight: 600;
}

select:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.select svg {
  position: absolute;
  top: 50%;
  right: 14px;
  transform: translateY(-50%);
  pointer-events: none;
  color: var(--text-secondary);
}
</style>
