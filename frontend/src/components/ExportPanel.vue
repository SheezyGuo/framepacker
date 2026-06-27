<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const format = ref('gif')
const exportFps = ref(10)
const exportResize = ref('')
const loop = ref(0)
const cols = ref(8)
const exporting = ref(false)
const cliCommand = ref('')

function getCliCommand() {
  if (!store.frameCount) return ''
  const parts = []
  if (format.value === 'gif') {
    parts.push('fp gif ./frames')
    parts.push(`--fps ${exportFps.value}`)
    if (exportResize.value) parts.push(`--resize ${exportResize.value}`)
    parts.push(`--loop ${loop.value}`)
    parts.push('--output animation.gif')
  } else if (format.value === 'png') {
    parts.push('zip -r frames.zip ./frames')
  } else if (format.value === 'sprite') {
    parts.push('fp sprite ./frames')
    parts.push(`--cols ${cols.value}`)
    if (exportResize.value) parts.push(`--resize ${exportResize.value}`)
    parts.push('--output sprite.png')
  }
  return '$ ' + parts.join(' ')
}

function showCommand() { cliCommand.value = getCliCommand() }

async function doExport() {
  exporting.value = true
  showCommand()
  setTimeout(() => { exporting.value = false }, 1000)
}
</script>

<template>
  <div class="export-panel">
    <h2>导出设置</h2>
    <div class="export-options">
      <div class="format-select">
        <label><input type="radio" v-model="format" value="gif" /><span>GIF 动图</span></label>
        <label><input type="radio" v-model="format" value="png" /><span>PNG 序列帧 (ZIP)</span></label>
        <label><input type="radio" v-model="format" value="sprite" /><span>精灵表 (Sprite Sheet)</span></label>
      </div>
      <div class="export-params">
        <label v-if="format === 'gif'">帧率 (FPS) <input v-model.number="exportFps" type="number" min="1" max="60" /></label>
        <label v-if="format === 'gif'">循环次数 (0=无限) <input v-model.number="loop" type="number" min="0" /></label>
        <label v-if="format === 'sprite'">列数 <input v-model.number="cols" type="number" min="1" max="20" /></label>
        <label>缩放 (留空=原始) <input v-model="exportResize" type="text" placeholder="如 512x512" /></label>
      </div>
    </div>
    <button :disabled="!store.frameCount || exporting" class="btn-primary" @click="doExport">
      {{ exporting ? '导出中...' : '生成导出命令' }}
    </button>
    <pre v-if="cliCommand" class="cli-command">{{ cliCommand }}</pre>
  </div>
</template>

<style scoped>
.export-panel { max-width: 600px; }
h2 { color: #1a1a2e; margin-bottom: 1rem; }
.export-options { margin-bottom: 1.5rem; }
.format-select { display: flex; gap: 1.5rem; margin-bottom: 1rem; }
.format-select label { display: flex; align-items: center; gap: 0.3rem; cursor: pointer; }
.export-params { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
.export-params label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.9rem; color: #555; }
.export-params input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px; }
.btn-primary { padding: 0.7rem 2rem; background: #ff6b35; color: #fff; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.cli-command { margin-top: 1rem; padding: 1rem; background: #1a1a2e; color: #0f0; border-radius: 8px; white-space: pre-wrap; font-family: monospace; }
</style>
