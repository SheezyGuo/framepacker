<script setup>
import { ref, computed } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const selectedIdx = ref(0)

const currentFrame = computed(() => {
  if (!store.frames.length) return null
  return store.frames[selectedIdx.value]
})

function prev() { if (selectedIdx.value > 0) selectedIdx.value-- }
function next() { if (selectedIdx.value < store.frames.length - 1) selectedIdx.value++ }
</script>

<template>
  <div class="frame-preview" v-if="currentFrame">
    <div class="preview-nav">
      <button @click="prev" :disabled="selectedIdx === 0">上一帧</button>
      <span>{{ selectedIdx + 1 }} / {{ store.frameCount }}</span>
      <button @click="next" :disabled="selectedIdx >= store.frames.length - 1">下一帧</button>
    </div>
    <div class="preview-image">
      <img :src="currentFrame" alt="Frame preview" />
    </div>
  </div>
  <div v-else class="preview-empty"><p>选择一帧以预览</p></div>
</template>

<style scoped>
.frame-preview { text-align: center; }
.preview-nav { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-bottom: 0.5rem; }
.preview-nav button { padding: 0.3rem 0.8rem; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; }
.preview-nav button:disabled { opacity: 0.4; cursor: not-allowed; }
.preview-image img { max-width: 100%; max-height: 400px; border: 1px solid #ddd; border-radius: 8px; }
.preview-empty { text-align: center; padding: 3rem; color: #999; }
</style>
