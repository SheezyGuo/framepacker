<script setup>
import { computed, watch } from 'vue'
import { useFrameStore } from '../stores/frames'
import { frameUrl } from '../api/framepacker'

const store = useFrameStore()

const currentFrame = computed(() => {
  if (!store.frames.length) return null
  return store.frames[store.previewIdx]
})

watch(() => store.frames.length, () => {
  if (store.previewIdx >= store.frames.length) store.setPreview(Math.max(0, store.frames.length - 1))
})

function prev() { if (store.previewIdx > 0) store.setPreview(store.previewIdx - 1) }
function next() { if (store.previewIdx < store.frames.length - 1) store.setPreview(store.previewIdx + 1) }
</script>

<template>
  <div class="panel frame-preview">
    <h2>单帧预览</h2>
    <div v-if="currentFrame">
      <div class="preview-nav">
        <button @click="prev" :disabled="store.previewIdx === 0">上一帧</button>
        <span>{{ store.previewIdx + 1 }} / {{ store.frameCount }}</span>
        <button @click="next" :disabled="store.previewIdx >= store.frames.length - 1">下一帧</button>
      </div>
      <div class="preview-image">
        <img :src="frameUrl(currentFrame)" alt="Frame preview" />
      </div>
    </div>
    <div v-else class="preview-empty"><p>选择一帧以预览</p></div>
  </div>
</template>

<style scoped>
.frame-preview { text-align: center; display: flex; flex-direction: column; }
.frame-preview h2 { font-size: 1rem; color: #1a1a2e; margin-bottom: 0.75rem; text-align: left; }
.preview-nav { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-bottom: 0.75rem; }
.preview-nav button { padding: 0.3rem 0.8rem; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; }
.preview-nav button:disabled { opacity: 0.4; cursor: not-allowed; }
.preview-image { flex: 1; display: flex; align-items: center; justify-content: center; min-height: 240px; }
.preview-image img { max-width: 100%; max-height: 300px; border: 1px solid #ddd; border-radius: 8px; }
.preview-empty { text-align: center; padding: 3rem; color: #999; }
</style>
