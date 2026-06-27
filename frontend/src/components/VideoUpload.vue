<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const videoUrl = ref(null)
const fileInput = ref(null)

function onFileSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  store.setVideo(file)
  videoUrl.value = URL.createObjectURL(file)
}

function triggerFileInput() {
  fileInput.value.click()
}
</script>

<template>
  <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="onFileSelected($event.dataTransfer)">
    <input ref="fileInput" type="file" accept="video/*" hidden @change="onFileSelected" />
    <div v-if="!store.videoFile" class="upload-placeholder">
      <p>拖拽视频到此处，或点击选择</p>
      <p class="hint">支持 MP4, AVI, MOV, WebM 等常见格式</p>
    </div>
    <div v-else class="upload-preview">
      <video :src="videoUrl" controls width="100%" />
      <p>{{ store.videoFile.name }} ({{ (store.videoFile.size / 1024 / 1024).toFixed(1) }} MB)</p>
      <button @click.stop="store.setVideo(null); videoUrl=null" class="btn-link">更换视频</button>
    </div>
  </div>
</template>

<style scoped>
.upload-area { border: 2px dashed #ccc; border-radius: 12px; padding: 3rem; text-align: center; cursor: pointer; background: #fafafa; }
.upload-area:hover { border-color: #ff6b35; }
.upload-placeholder p { font-size: 1.1rem; color: #666; }
.hint { font-size: 0.85rem; color: #999; margin-top: 0.5rem; }
.upload-preview p { margin-top: 0.5rem; color: #555; }
.btn-link { background: none; border: none; color: #ff6b35; cursor: pointer; text-decoration: underline; margin-top: 0.5rem; }
</style>
