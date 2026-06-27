<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'
import { extractFrames as apiExtract } from '../api/framepacker'

const store = useFrameStore()
const fps = ref(12)
const duration = ref(null)
const start = ref(0)
const resize = ref('')
const extracting = ref(false)
const progress = ref('')
const error = ref('')

async function extractFrames() {
  if (!store.videoFile) return
  extracting.value = true
  error.value = ''
  progress.value = '提取中...'

  try {
    const result = await apiExtract({
      videoPath: store.videoFile.name,
      fps: fps.value,
      output: './frames',
      start: start.value,
      duration: duration.value || null,
      resize: resize.value || null,
    })
    store.addFrames(result.frames)
    progress.value = `成功提取 ${result.count} 帧`
  } catch (e) {
    error.value = `提取失败: ${e.message}`
  } finally {
    extracting.value = false
  }
}
</script>

<template>
  <div class="extractor">
    <h2>提取参数</h2>
    <div class="form-row">
      <label>帧率 (FPS) <input v-model.number="fps" type="number" min="1" max="60" /></label>
      <label>起始时间 (秒) <input v-model.number="start" type="number" min="0" step="0.1" /></label>
      <label>时长 (秒, 留空=全部) <input v-model.number="duration" type="number" min="0" step="0.1" placeholder="全部" /></label>
      <label>缩放 (留空=原始) <input v-model="resize" type="text" placeholder="如 512x512" /></label>
    </div>
    <button :disabled="!store.videoFile || extracting" class="btn-primary" @click="extractFrames">
      {{ extracting ? '提取中...' : '提取帧' }}
    </button>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="progress && !error" class="progress">{{ progress }}</p>
  </div>
</template>

<style scoped>
.extractor { margin-top: 2rem; }
h2 { color: #1a1a2e; margin-bottom: 1rem; }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.9rem; color: #555; }
input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; }
.btn-primary { padding: 0.7rem 2rem; background: #ff6b35; color: #fff; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.error { margin-top: 0.5rem; color: #d32f2f; }
.progress { margin-top: 0.5rem; color: #2e7d32; }
</style>
