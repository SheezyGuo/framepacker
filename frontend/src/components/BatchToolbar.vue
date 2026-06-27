<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const threshold = ref(0.92)

function runDedup() {
  const indices = [...store.selectedFrames].length
    ? [...store.selectedFrames].sort((a, b) => b - a) : []
  if (indices.length <= 1) return
  for (let i = 1; i < indices.length; i++) store.removeFrame(indices[i])
  store.deselectAll()
}

function removeBg() { alert('批量抠图功能需要 CLI: fp remove-bg ./frames') }
function grayscaleAll() { alert('批量转灰度需要 CLI: fp edit ./frames --grayscale') }
</script>

<template>
  <div class="batch-toolbar">
    <h4>批量操作</h4>
    <div class="tool-group">
      <label>去重阈值</label>
      <input v-model.number="threshold" type="number" min="0" max="1" step="0.01" />
      <button @click="runDedup" :disabled="store.selectedCount < 2">去重选中</button>
    </div>
    <div class="tool-group">
      <button @click="store.selectAll">全选</button>
      <button @click="removeBg">批量抠图</button>
      <button @click="grayscaleAll">批量灰度</button>
    </div>
  </div>
</template>

<style scoped>
.batch-toolbar { padding: 1rem; background: #fff; border-radius: 8px; margin-bottom: 1rem; }
h4 { margin-bottom: 0.5rem; color: #1a1a2e; }
.tool-group { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; margin-bottom: 0.5rem; }
.tool-group input { width: 80px; padding: 0.3rem; border: 1px solid #ddd; border-radius: 4px; }
.tool-group button { padding: 0.3rem 0.8rem; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; }
.tool-group button:hover { background: #f0f0f0; }
</style>
