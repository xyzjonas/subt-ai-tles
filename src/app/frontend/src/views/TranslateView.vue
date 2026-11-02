<script setup lang="ts">
import FileDropZone from "../components/landing/FileDropZone.vue";
import HeroSection from "../components/landing/HeroSection.vue";
import LanguagePairing from "../components/landing/LanguagePairing.vue";
import RecentJobs from "../components/landing/RecentJobs.vue";
import TranslateAction from "../components/landing/TranslateAction.vue";
import { useTranslateForm } from "../composables/useTranslateForm";

const form = useTranslateForm();
const { srt } = form;
</script>

<template>
  <div class="page">
    <HeroSection />
    <FileDropZone
      :entries="srt.entries.value"
      :errors="srt.errors.value"
      :loading="srt.loading.value"
      @select="srt.add"
      @remove="srt.remove"
    />
    <LanguagePairing
      :target-code="form.targetCode.value"
      :languages="form.languages.value"
      @update:target-code="form.setTarget"
    />
    <TranslateAction
      :estimate="form.estimate.value"
      :disabled="!form.canSubmit.value"
      :submitting="form.submitting.value"
      :error="form.submitError.value"
      @submit="form.submit"
    />
    <RecentJobs class="recent" />
  </div>
</template>

<style scoped>
.page {
  display: grid;
  gap: 24px;
}

.recent {
  margin-top: 8px;
}
</style>
