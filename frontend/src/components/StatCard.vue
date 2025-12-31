<template>
  <Card class="p-4">
    <div class="grid grid-cols-4 gap-4">
      <div>
        <p class="text-xs text-slate-600 dark:text-slate-400 mb-1">{{ title }}</p>
        <p class="text-2xl font-bold" :class="textColor">{{ value }}</p>
      </div>
      <div class="col-span-3 flex items-end justify-end">
        <!-- Se tiver slot (SVG), usa o slot. Senão usa o icon -->
        <slot v-if="$slots.default" />
        <span v-else class="text-4xl opacity-50" v-html="icon" />
      </div>
    </div>
  </Card>
</template>

<script setup>
import { computed } from 'vue'
import Card from './Card.vue'

const props = defineProps({
  title: String,
  value: [String, Number],
  icon: String,
  color: {
    type: String,
    default: 'sky'
  }
})

const textColor = computed(() => {
  const colors = {
    sky: 'text-sky-600 dark:text-sky-400',
    green: 'text-emerald-600 dark:text-emerald-400',
    red: 'text-rose-600 dark:text-rose-400',
    blue: 'text-sky-600 dark:text-sky-400',
    purple: 'text-violet-600 dark:text-violet-400'
  }
  return colors[props.color]
})
</script>
