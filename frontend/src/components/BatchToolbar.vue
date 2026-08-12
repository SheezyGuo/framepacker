<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'
import { cleanupWorkspace, detectDupes, detectJumps, removeBg, batchEdit } from '../api/framepacker'

const store = useFrameStore()
const threshold = ref(0.92)
const jumpThreshold = ref(0.4)
const cleaning = ref(false)
const detecting = ref(false)
const jumping = ref(false)
const processing = ref(false)
const detectMsg = ref('')
const bgColor = ref('#ffffff')

function framesDir() {
  if (!store.frames.length) return null
  const first = store.frames[0]
  const slash = Math.max(first.lastIndexOf('/'), first.lastIndexOf('\\'))
  return slash >= 0 ? first.slice(0, slash) : null
}

async function runDetect() {
  const dir = framesDir()
  if (!dir || !store.frameCount) return
  detecting.value = true
  detectMsg.value = ''
  try {
    const result = await detectDupes({ framesDir: dir, threshold: threshold.value })
    const dupes = new Set(result.dupes)
    store.deselectAll()
    store.frames.forEach((f, idx) => {
      if (!dupes.has(f)) store.selectedFrames.add(idx)
    })
    detectMsg.value = `检测到 ${result.count} 帧重复,已选中保留的 ${store.selectedCount} 帧,可微调后点击「去重」`
  } catch (e) {
    detectMsg.value = `检测失败: ${e.message}`
  } finally {
    detecting.value = false
  }
}

async function runJumpDetect() {
  const dir = framesDir()
  if (!dir || !store.frameCount) return
  jumping.value = true
  detectMsg.value = ''
  try {
    const result = await detectJumps({ framesDir: dir, threshold: jumpThreshold.value })
    const jumps = new Set(result.jumps)
    store.deselectAll()
    store.frames.forEach((f, idx) => {
      if (jumps.has(f)) store.selectedFrames.add(idx)
    })
    detectMsg.value = `定位到 ${result.count} 帧跳变,已选中`
  } catch (e) {
    detectMsg.value = `定位失败: ${e.message}`
  } finally {
    jumping.value = false
  }
}

function runDedup() {
  if (!store.selectedCount) return
  const keep = new Set([...store.selectedFrames])
  const removeIndices = store.frames.map((_, idx) => idx).filter((idx) => !keep.has(idx))
  for (const idx of removeIndices.sort((a, b) => b - a)) store.removeFrame(idx)
  store.deselectAll()
  detectMsg.value = ''
}

async function runRemoveBg() {
  const dir = framesDir()
  if (!dir || !store.frameCount) return
  processing.value = true
  detectMsg.value = ''
  try {
    const result = await removeBg({ framesDir: dir })
    store.clearFrames()
    store.addFrames(result.frames)
    detectMsg.value = `已为 ${result.count} 帧去除背景`
  } catch (e) {
    detectMsg.value = `抠图失败: ${e.message}`
  } finally {
    processing.value = false
  }
}

async function runGrayscale() {
  const dir = framesDir()
  if (!dir || !store.frameCount) return
  processing.value = true
  detectMsg.value = ''
  try {
    const result = await batchEdit({ framesDir: dir, grayscale: true })
    store.clearFrames()
    store.addFrames(result.frames)
    detectMsg.value = `已为 ${result.count} 帧转为灰度`
  } catch (e) {
    detectMsg.value = `灰度失败: ${e.message}`
  } finally {
    processing.value = false
  }
}

async function runChangeBg() {
  const dir = framesDir()
  if (!dir || !store.frameCount) return
  processing.value = true
  detectMsg.value = ''
  try {
    const result = await batchEdit({ framesDir: dir, background: bgColor.value })
    store.clearFrames()
    store.addFrames(result.frames)
    detectMsg.value = `已将 ${result.count} 帧背景替换为 ${bgColor.value}`
  } catch (e) {
    detectMsg.value = `换背景失败: ${e.message}`
  } finally {
    processing.value = false
  }
}

async function clearAll() {
  if (!confirm('确定清空工作区?所有已提取的任务文件将被删除。')) return
  cleaning.value = true
  try {
    await cleanupWorkspace()
    store.clearFrames()
  } catch (e) {
    alert(`清空失败: ${e.message}`)
  } finally {
    cleaning.value = false
  }
}
</script>

<template>
  <div class="batch-toolbar">
    <h4>批量操作</h4>
    <div class="section">
      <span class="section-label">选择</span>
      <div class="btn-row">
        <button @click="store.selectAll" :disabled="!store.frameCount">全选</button>
        <button @click="store.deselectAll" :disabled="!store.selectedCount">取消选择</button>
      </div>
    </div>
    <div class="section">
      <span class="section-label">检测</span>
      <div class="btn-row">
        <label class="inline-label">帧相似度
          <input v-model.number="threshold" type="number" min="0" max="1" step="0.01" />
        </label>
        <button @click="runDetect" :disabled="detecting || !store.frameCount">{{ detecting ? '检测中...' : '检测重复' }}</button>
        <label class="inline-label">跳变阈值
          <input v-model.number="jumpThreshold" type="number" min="0" max="1" step="0.01" />
        </label>
        <button @click="runJumpDetect" :disabled="jumping || !store.frameCount">{{ jumping ? '定位中...' : '定位跳变帧' }}</button>
      </div>
    </div>
    <div class="section">
      <span class="section-label">处理</span>
      <div class="btn-row">
        <button class="danger" @click="runDedup" :disabled="!store.selectedCount">去重(删除未选中)</button>
        <button @click="runRemoveBg" :disabled="processing || !store.frameCount">{{ processing ? '处理中...' : '批量抠图' }}</button>
        <button @click="runGrayscale" :disabled="processing || !store.frameCount">批量灰度</button>
        <label class="inline-label">背景色
          <input v-model="bgColor" type="color" />
          <input v-model="bgColor" class="color-text" size="8" />
        </label>
        <button @click="runChangeBg" :disabled="processing || !store.frameCount">换背景</button>
      </div>
    </div>
    <div v-if="detectMsg" class="detect-msg">{{ detectMsg }}</div>
    <div class="divider"></div>
    <div class="section">
      <span class="section-label">危险</span>
      <div class="btn-row">
        <button class="danger" @click="clearAll" :disabled="cleaning">{{ cleaning ? '清理中...' : '清空工作区' }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.batch-toolbar { padding: 1rem; background: #fff; border-radius: 8px; margin-bottom: 1rem; }
h4 { margin-bottom: 0.75rem; color: #1a1a2e; }
.section { display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 0.75rem; }
.section-label { font-size: 0.75rem; color: #999; text-transform: uppercase; letter-spacing: 0.05em; }
.btn-row { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
.btn-row button { padding: 0.35rem 0.8rem; border: 1px solid #ddd; background: #fff; border-radius: 6px; cursor: pointer; font-size: 0.9rem; transition: all 0.15s; }
.btn-row button:hover:not(:disabled) { background: #f0f0f0; }
.btn-row button:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-row .danger { color: #d32f2f; border-color: #d32f2f; }
.btn-row .danger:hover:not(:disabled) { background: #fdecea; }
.inline-label { display: flex; align-items: center; gap: 0.3rem; font-size: 0.85rem; color: #555; }
.inline-label input[type="number"] { width: 64px; padding: 0.3rem; border: 1px solid #ddd; border-radius: 6px; }
.inline-label input[type="color"] { width: 36px; height: 26px; padding: 0; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; }
.color-text { width: 64px; padding: 0.3rem; border: 1px solid #ddd; border-radius: 6px; }
.divider { border-top: 1px solid #eee; margin-bottom: 0.75rem; }
.detect-msg { font-size: 0.8rem; color: #ff6b35; margin-bottom: 0.75rem; }
</style>
