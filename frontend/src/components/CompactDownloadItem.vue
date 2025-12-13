<template>
  <Card class="p-4">
    <div class="flex items-start justify-between gap-4">
      <div class="flex-1">
        <h4 class="font-semibold text-white">{{ job.item_name || 'Download' }}</h4>
        <p class="text-xs text-slate-400 mt-1">{{ downloadStore.formatProgress(Math.min(job.progress || 0, 100)) }}% - {{ formatBytes(job.downloaded || 0) }} {{ job.total ? '/ ' + formatBytes(job.total) : '' }}</p>
      </div>
      <span :style="{ color: getStatusColor(job.status) }" class="text-xs font-semibold px-2 py-1 bg-slate-900/50 rounded">
        {{ getStatusLabel(job.status) }}
      </span>
    </div>
    <div class="w-full h-1 rounded-full bg-slate-700 mt-3 overflow-hidden">
      <div
        class="h-full bg-gradient-to-r from-cyan-500 to-blue-600"
        :style="{ width: Math.min(job.progress || 0, 100) + '%' }"
      />
    </div>
    <div class="flex gap-2 mt-3">
      <Button
        v-if="status === 'failed'"
        variant="success"
        size="sm"
        class="flex-1"
        @click="$emit('retry')"
      >
        Retry
      </Button>
      <router-link v-else to="/downloads" class="flex-1">
        <Button variant="outline" size="sm" class="w-full btn-translucent">Ver</Button>
      </router-link>
    </div>
  </Card>
</template>

<script setup>
import Card from './Card.vue'
import Button from './Button.vue'
import { formatBytes, getStatusColor, getStatusLabel } from '../utils/format'

defineProps({
  job: Object,
  status: String
})

defineEmits(['retry'])
</script>
