<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useFrameStore } from '../stores/frames'
import { frameUrl, saveFrame } from '../api/framepacker'

const store = useFrameStore()
const canvasRef = ref(null)
const tool = ref('brush')
const brushColor = ref('#ff0000')
const brushSize = ref(8)
const filterType = ref('none')
const filterAmount = ref(50)
const saving = ref(false)
const savingAll = ref(false)
const msg = ref('')

const undoStack = []
const MAX_UNDO = 20
let drawing = false
let loaded = false

watch(() => store.frames.length, () => { if (store.frames.length > 0) loadFrame(store.previewIdx) })
watch(() => store.previewIdx, (idx) => { if (store.frames.length > 0) loadFrame(idx) })

function ctx2d() { return canvasRef.value?.getContext('2d') }

function loadFrame(idx) {
  loaded = false
  const canvas = canvasRef.value
  if (!canvas || !store.frames[idx]) return
  const img = new Image()
  img.onload = () => {
    canvas.width = img.width
    canvas.height = img.height
    ctx2d().clearRect(0, 0, canvas.width, canvas.height)
    ctx2d().drawImage(img, 0, 0)
    loaded = true
    undoStack.length = 0
  }
  img.crossOrigin = 'anonymous'
  img.src = frameUrl(store.frames[idx])
}

function pos(e) {
  const rect = canvasRef.value.getBoundingClientRect()
  return {
    x: (e.clientX - rect.left) * (canvasRef.value.width / rect.width),
    y: (e.clientY - rect.top) * (canvasRef.value.height / rect.height),
  }
}

function pushUndo() {
  const data = ctx2d().getImageData(0, 0, canvasRef.value.width, canvasRef.value.height)
  undoStack.push(data)
  if (undoStack.length > MAX_UNDO) undoStack.shift()
}

function undo() {
  if (!loaded || !undoStack.length) return
  ctx2d().putImageData(undoStack.pop(), 0, 0)
}

function onPointerDown(e) {
  if (!loaded) return
  drawing = true
  canvasRef.value.setPointerCapture(e.pointerId)
  pushUndo()
  stroke(e)
}

function onPointerMove(e) {
  if (!drawing) return
  stroke(e)
}

function onPointerUp() { drawing = false }

function stroke(e) {
  const c = ctx2d()
  const { x, y } = pos(e)
  c.globalCompositeOperation = tool.value === 'eraser' ? 'destination-out' : 'source-over'
  c.fillStyle = brushColor.value
  c.beginPath()
  c.arc(x, y, tool.value === 'eraser' ? brushSize.value : brushSize.value / 2, 0, Math.PI * 2)
  c.fill()
  c.globalCompositeOperation = 'source-over'
}

function applyFilter() {
  if (!loaded) return
  const c = ctx2d()
  let filter = ''
  if (filterType.value === 'grayscale') filter = 'grayscale(1)'
  else if (filterType.value === 'invert') filter = 'invert(1)'
  else if (filterType.value === 'brightness') filter = `brightness(${0.5 + filterAmount.value / 100})`
  else if (filterType.value === 'contrast') filter = `contrast(${0.5 + filterAmount.value / 100})`
  else if (filterType.value === 'blur') filter = `blur(${filterAmount.value / 10}px)`
  if (!filter) return
  pushUndo()
  c.filter = filter
  c.drawImage(canvasRef.value, 0, 0)
  c.filter = 'none'
}

async function saveCurrent() {
  if (!loaded) return
  saving.value = true
  msg.value = ''
  try {
    const dataUrl = canvasRef.value.toDataURL('image/png')
    await saveFrame({ path: store.frames[store.previewIdx], data: dataUrl })
    msg.value = `第 ${store.previewIdx + 1} 帧已保存`
  } catch (e) {
    msg.value = `保存失败: ${e.message}`
  } finally {
    saving.value = false
  }
}

async function saveAll() {
  if (!store.frames.length) return
  savingAll.value = true
  msg.value = ''
  try {
    const { frames } = store
    for (let i = 0; i < frames.length; i++) {
      const img = await loadImage(frames[i])
      const cv = document.createElement('canvas')
      cv.width = img.width
      cv.height = img.height
      const c = cv.getContext('2d')
      if (filterType.value !== 'none' && filterType.value !== '') {
        let filter = ''
        if (filterType.value === 'grayscale') filter = 'grayscale(1)'
        else if (filterType.value === 'invert') filter = 'invert(1)'
        else if (filterType.value === 'brightness') filter = `brightness(${0.5 + filterAmount.value / 100})`
        else if (filterType.value === 'contrast') filter = `contrast(${0.5 + filterAmount.value / 100})`
        else if (filterType.value === 'blur') filter = `blur(${filterAmount.value / 10}px)`
        c.filter = filter
      }
      c.drawImage(img, 0, 0)
      await saveFrame({ path: frames[i], data: cv.toDataURL('image/png') })
      await new Promise((r) => setTimeout(r, 50))
    }
    await loadFrame(store.previewIdx)
    msg.value = `已应用并保存全部 ${frames.length} 帧`
  } catch (e) {
    msg.value = `批量保存失败: ${e.message}`
  } finally {
    savingAll.value = false
  }
}

function loadImage(path) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.crossOrigin = 'anonymous'
    img.src = frameUrl(path)
  })
}

function resetFilter() { filterType.value = 'none' }

onMounted(() => { if (store.frames.length > 0) loadFrame(store.previewIdx) })
onUnmounted(() => { drawing = false })
</script>

<template>
  <div class="panel frame-canvas">
    <div class="canvas-header">
      <h4>逐帧精修</h4>
      <span class="frame-info" v-if="store.frames.length">当前:第 {{ store.previewIdx + 1 }} / {{ store.frameCount }} 帧</span>
    </div>

    <div class="toolbar">
      <div class="tool-group">
        <button :class="{ active: tool === 'brush' }" @click="tool = 'brush'">画笔</button>
        <button :class="{ active: tool === 'eraser' }" @click="tool = 'eraser'">橡皮</button>
        <input v-if="tool === 'brush'" v-model="brushColor" type="color" title="画笔颜色" />
        <label>粗细
          <input v-model.number="brushSize" type="range" min="1" max="60" />
        </label>
        <button @click="undo" :disabled="!undoStack.length">撤销</button>
      </div>

      <div class="tool-group">
        <select v-model="filterType">
          <option value="none">无滤镜</option>
          <option value="grayscale">灰度</option>
          <option value="invert">反相</option>
          <option value="brightness">亮度</option>
          <option value="contrast">对比度</option>
          <option value="blur">模糊</option>
        </select>
        <label v-if="filterType === 'brightness' || filterType === 'contrast' || filterType === 'blur'">
          强度 <input v-model.number="filterAmount" type="range" min="0" max="100" />
        </label>
        <button @click="applyFilter" :disabled="filterType === 'none'">应用滤镜</button>
      </div>
    </div>

    <div class="canvas-wrap">
      <canvas ref="canvasRef" class="editor-canvas"
        @pointerdown="onPointerDown" @pointermove="onPointerMove" @pointerup="onPointerUp" @pointerleave="onPointerUp"></canvas>
    </div>

    <div class="actions">
      <button class="btn-primary" @click="saveCurrent" :disabled="saving || !loaded">{{ saving ? '保存中...' : '保存当前帧' }}</button>
      <button @click="saveAll" :disabled="savingAll || !store.frameCount">{{ savingAll ? '批量保存中...' : '应用滤镜到全部帧' }}</button>
      <button @click="resetFilter">清除滤镜</button>
    </div>
    <p v-if="msg" class="msg">{{ msg }}</p>
  </div>
</template>

<style scoped>
.frame-canvas { margin-top: 1rem; }
.canvas-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
h4 { margin: 0; color: #1a1a2e; }
.frame-info { font-size: 0.85rem; color: #777; }
.toolbar { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0.75rem; }
.tool-group { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.tool-group button, .tool-group select { padding: 0.3rem 0.7rem; border: 1px solid #ddd; background: #fff; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.tool-group button:hover { background: #f0f0f0; }
.tool-group button.active { background: #ff6b35; color: #fff; border-color: #ff6b35; }
.tool-group button:disabled { opacity: 0.4; cursor: not-allowed; }
.tool-group input[type="color"] { width: 34px; height: 26px; padding: 0; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; }
.tool-group label { display: flex; align-items: center; gap: 0.3rem; font-size: 0.85rem; color: #555; }
.tool-group input[type="range"] { width: 80px; }
.canvas-wrap { display: flex; justify-content: center; background: repeating-conic-gradient(#eee 0 25%, #fff 0 50%) 0 0 / 16px 16px; border: 1px solid #ddd; border-radius: 8px; padding: 8px; }
.editor-canvas { max-width: 100%; touch-action: none; cursor: crosshair; background: #fff; }
.actions { display: flex; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap; }
.actions button { padding: 0.4rem 1rem; border: 1px solid #ddd; background: #fff; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
.actions button:hover { background: #f0f0f0; }
.actions .btn-primary { background: #ff6b35; color: #fff; border-color: #ff6b35; }
.actions .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.msg { font-size: 0.85rem; color: #2e7d32; margin-top: 0.5rem; }
</style>
