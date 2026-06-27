<script setup>
import { ref, onMounted, watch } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const canvasRef = ref(null)
const selectedIdx = ref(0)

watch(() => store.frames.length, () => { if (store.frames.length > 0) loadFrame(0) })

function loadFrame(idx) {
  selectedIdx.value = idx
  if (!canvasRef.value || !store.frames[idx]) return
  const img = new Image()
  img.onload = () => {
    const canvas = canvasRef.value
    canvas.width = img.width
    canvas.height = img.height
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0)
  }
  img.src = store.frames[idx]
}
</script>

<template>
  <div class="frame-canvas">
    <h4>逐帧精修</h4>
    <canvas ref="canvasRef" class="editor-canvas"></canvas>
    <p class="hint">提示：完整 Canvas 编辑功能（画笔/裁剪/滤镜）将在后续版本实现</p>
  </div>
</template>

<style scoped>
.frame-canvas { margin-top: 1rem; }
h4 { margin-bottom: 0.5rem; color: #1a1a2e; }
.editor-canvas { max-width: 100%; border: 1px solid #ddd; border-radius: 8px; background: #fff; }
.hint { font-size: 0.85rem; color: #999; margin-top: 0.5rem; }
</style>
