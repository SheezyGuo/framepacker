<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'
import { framesToGif, framesToSprite } from '../api/framepacker'

const store = useFrameStore()
const format = ref('gif')
const exportFps = ref(10)
const exportResize = ref('')
const loop = ref(0)
const cols = ref(8)
const exporting = ref(false)
const result = ref('')
const error = ref('')

async function doExport() {
  exporting.value = true
  error.value = ''
  result.value = ''
  try {
    if (format.value === 'gif') {
      const res = await framesToGif({ framesDir: './frames', fps: exportFps.value, output: 'animation.gif', resize: exportResize.value || null, loop: loop.value })
      result.value = `GIF 已保存: ${res.output}`
    } else if (format.value === 'sprite') {
      const res = await framesToSprite({ framesDir: './frames', cols: cols.value, output: 'sprite.png', resize: exportResize.value || null })
      result.value = `精灵表已保存: ${res.output}`
    } else {
      result.value = 'PNG 序列帧需手动打包: fp pipeline pack.yaml'
    }
  } catch (e) {
    error.value = `导出失败: ${e.message}`
  } finally {
    exporting.value = false
  }
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
        <label v-if="format === 'gif'">循环次数 <input v-model.number="loop" type="number" min="0" /></label>
        <label v-if="format === 'sprite'">列数 <input v-model.number="cols" type="number" min="1" max="20" /></label>
        <label>缩放 <input v-model="exportResize" type="text" placeholder="如 512x512" /></label>
      </div>
    </div>
    <button :disabled="!store.frameCount || exporting" class="btn-primary" @click="doExport">
      {{ exporting ? '导出中...' : '开始导出' }}
    </button>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="result" class="success">{{ result }}</p>
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
.error { margin-top: 0.5rem; color: #d32f2f; }
.success { margin-top: 0.5rem; color: #2e7d32; }
</style>
