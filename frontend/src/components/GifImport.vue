<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'
import { importGif } from '../api/framepacker'

const store = useFrameStore()
const importing = ref(false)
const progress = ref('')
const error = ref('')
const fileInput = ref(null)

function triggerFileInput() {
  fileInput.value.click()
}

async function onFileSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  importing.value = true
  error.value = ''
  progress.value = '导入中...'
  try {
    const result = await importGif(file)
    store.setVideo(file)
    store.clearFrames()
    store.addFrames(result.frames)
    progress.value = `成功导入 ${result.count} 帧`
  } catch (err) {
    error.value = `导入失败: ${err.message}`
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <div class="gif-import">
    <h3>从 GIF 导入</h3>
    <input ref="fileInput" type="file" accept=".gif" hidden @change="onFileSelected" />
    <div class="import-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="onFileSelected($event.dataTransfer)">
      <p v-if="!importing">点击选择或拖拽 GIF 文件导入为帧序列</p>
      <p v-else>{{ progress }}</p>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="progress && !error && !importing" class="progress">{{ progress }}</p>
  </div>
</template>

<style scoped>
.gif-import { margin-top: 2rem; }
h3 { color: #1a1a2e; margin-bottom: 0.75rem; }
.import-area { border: 2px dashed #ccc; border-radius: 12px; padding: 2rem; text-align: center; cursor: pointer; background: #fafafa; color: #666; }
.import-area:hover { border-color: #ff6b35; }
.error { margin-top: 0.5rem; color: #d32f2f; }
.progress { margin-top: 0.5rem; color: #2e7d32; }
</style>
