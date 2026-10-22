<script setup lang="ts">
// Subset of the app's AppIcon paths, so the preview draws the same glyphs.
const PATHS = {
  file: "M14 3H7a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V7l-4-4Zm0 0v4h4",
  check: "m5 12 5 5 9-10",
  close: "M6 6l12 12M18 6 6 18",
  back: "M19 12H5m6-6-6 6 6 6",
  copy: "M9 9h10v11H9V9Zm-4 6V4h10",
  edit: "M4 20h4L19 9l-4-4L4 16v4Zm9-13 4 4",
  flag: "M6 21V4m0 0h11l-2 4 2 4H6",
  sparkle: "M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z",
  play: "M8 5v14l11-7L8 5Z",
  retry: "M4 12a8 8 0 1 0 3-6.2M4 4v5h5",
  search: "M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14Zm5-2 4 4",
  download: "M12 4v12m0 0 5-5m-5 5-5-5M4 20h16",
  sync: "M20 11a8 8 0 0 0-14-4M4 4v4h4M4 13a8 8 0 0 0 14 4m2 3v-4h-4",
} as const;

export type PreviewIconName = keyof typeof PATHS;

withDefaults(defineProps<{ name: PreviewIconName; size?: number }>(), { size: 20 });
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path :d="PATHS[name]" />
  </svg>
</template>
