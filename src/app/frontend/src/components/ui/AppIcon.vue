<script setup lang="ts">
const PATHS = {
  upload: "M12 16V4m0 0L7 9m5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3",
  file: "M14 3H7a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V7l-4-4Zm0 0v4h4",
  globe: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0 0c2.5-2.5 3.5-5.5 3.5-9S14.500 5.500 12 3m0 18c-2.500-2.500-3.500-5.500-3.500-9S9.500 5.500 12 3M3 12h18",
  close: "M6 6l12 12M18 6 6 18",
  swap: "M8 4v16m0 0-3-3m3 3 3-3M16 20V4m0 0-3 3m3-3 3 3",
  chevron: "m6 9 6 6 6-6",
  clock: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0-13v4l3 2",
  user: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-7 8a7 7 0 0 1 14 0",
  translate: "M4 5h9M8.500 3v2m3.500 0c-.5 4-3 7-7 9m2-6c1 2 3 4.500 6 5.500M13 20l4-9 4 9m-6.800-3h5.600",
  list: "M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01",
  bolt: "M13 3 5 14h6l-1 7 8-11h-6l1-7Z",
  gear: "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm0-12v3m0 12v3M3 12h3m12 0h3M5.600 5.600l2.100 2.100m8.600 8.600 2.100 2.100m0-12.800-2.100 2.100M7.700 16.300l-2.100 2.100",
  arrow: "M5 12h14m-6-6 6 6-6 6",
  search: "M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14Zm5-2 4 4",
  download: "M12 4v12m0 0 5-5m-5 5-5-5M4 20h16",
  next: "m9 6 6 6-6 6",
  sync: "M20 11a8 8 0 0 0-14-4M4 4v4h4M4 13a8 8 0 0 0 14 4m2 3v-4h-4",
  check: "m5 12 5 5 9-10",
  chat: "M4 5h16v11H9l-5 4V5Z",
  back: "M19 12H5m6-6-6 6 6 6",
  copy: "M9 9h10v11H9V9Zm-4 6V4h10",
  share: "M12 16V4m0 0L7 9m5-5 5 5M5 14v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5",
  edit: "M4 20h4L19 9l-4-4L4 16v4Zm9-13 4 4",
  flag: "M6 21V4m0 0h11l-2 4 2 4H6",
  sparkle: "M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z",
  play: "M8 5v14l11-7L8 5Z",
  terminal: "M4 5h16v14H4V5Zm4 4 3 3-3 3m5 0h4",
  bell: "M6 16V11a6 6 0 1 1 12 0v5l2 2H4l2-2Zm4 4a2 2 0 0 0 4 0",
  stop: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18ZM9 9l6 6m0-6-6 6",
  alert: "M12 4 3 20h18L12 4Zm0 6v4m0 3h.01",
  retry: "M4 12a8 8 0 1 0 3-6.2M4 4v5h5",
} as const;

export type IconName = keyof typeof PATHS;

withDefaults(defineProps<{ name: IconName; size?: number }>(), { size: 20 });
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path :d="PATHS[name]" />
  </svg>
</template>
