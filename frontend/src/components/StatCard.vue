<template>
  <Card class="p-4">
    <div class="grid grid-cols-4 gap-4">
      <div>
        <p class="text-xs text-slate-400 mb-1">{{ title }}</p>
        <p class="text-2xl font-bold" :class="textColor">{{ value }}</p>
      </div>
      <div class="col-span-3 flex items-end justify-end">
        <!-- Se tiver slot (SVG), usa o slot. Senão usa o icon -->
        <slot v-if="$slots.default" />
        <span v-else class="text-4xl" v-html="icon" />
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
    default: 'cyan'
  }
})

const textColor = computed(() => {
  const colors = {
    cyan: 'text-cyan-300',
    green: 'text-green-300',
    red: 'text-red-300',
    blue: 'text-blue-300',
    purple: 'text-purple-300'
  }
  return colors[props.color]
})
</script>
