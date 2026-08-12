<script setup>
import { useFrameStore } from '../stores/frames'
import { frameUrl } from '../api/framepacker'

const store = useFrameStore()

function onDragStart(e, idx) {
  e.dataTransfer.setData('text/plain', idx)
}
function onDrop(e, idx) {
  const from = parseInt(e.dataTransfer.getData('text/plain'))
  if (from !== idx) store.moveFrame(from, idx)
}
function onToggleSelect(e, idx) {
  e.stopPropagation()
  store.toggleSelect(idx)
}
function onQuickDelete(e, idx) {
  e.stopPropagation()
  if (confirm(`删除第 ${idx + 1} 帧?`)) {
    store.removeFrame(idx)
    store.setPreview(Math.min(store.previewIdx, store.frames.length - 2))
  }
}
</script>

<template>
  <div class="frame-list">
    <div class="list-header">
      <h3>帧列表 ({{ store.frameCount }})</h3>
      <div class="list-actions">
        <button @click="store.selectAll" :disabled="!store.frameCount">全选</button>
        <button @click="store.deselectAll" :disabled="!store.selectedCount">取消选择</button>
        <button @click="store.removeSelected" :disabled="!store.selectedCount">删除选中</button>
      </div>
    </div>
    <div class="frame-grid">
      <div v-for="(frame, idx) in store.frames" :key="idx"
        class="frame-thumb" :class="{ selected: store.selectedFrames.has(idx) }"
        draggable="true"
        @dragstart="onDragStart($event, idx)"
        @dragover.prevent @drop="onDrop($event, idx)"
        @click="store.toggleSelect(idx); store.setPreview(idx)">
        <span class="select-box" :class="{ checked: store.selectedFrames.has(idx) }" @click="onToggleSelect($event, idx)"></span>
        <button class="del-btn" @click="onQuickDelete($event, idx)">×</button>
        <img :src="frameUrl(frame)" :alt="'Frame ' + idx" />
        <span class="frame-idx">{{ idx + 1 }}</span>
      </div>
    </div>
    <div v-if="!store.frameCount" class="empty">
      <p>暂无帧数据。请先提取视频帧。</p>
      <router-link to="/extract">前往提取帧</router-link>
    </div>
  </div>
</template>

<style scoped>
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.list-actions { display: flex; gap: 0.5rem; }
.list-actions button { padding: 0.3rem 0.8rem; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; }
.frame-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(64px, 1fr)); gap: 0.4rem; }
.frame-thumb { position: relative; border: 2px solid transparent; border-radius: 6px; cursor: pointer; transition: border-color 0.2s; background: #f5f5f5; display: flex; align-items: center; justify-content: center; padding: 3px; }
.frame-thumb:hover { border-color: #ff6b35; }
.frame-thumb.selected { border-color: #1a1a2e; background: #e0e0e0; }
.frame-thumb img { width: 100%; height: auto; max-height: 90px; object-fit: contain; border-radius: 4px; display: block; }
.select-box {
  position: absolute; top: 5px; left: 5px; width: 16px; height: 16px;
  border: 2px solid #fff; border-radius: 3px; background: rgba(0,0,0,0.35);
  box-shadow: 0 0 2px rgba(0,0,0,0.5); z-index: 2; cursor: pointer;
}
.select-box.checked { background: #ff6b35; border-color: #fff; }
.select-box.checked::after {
  content: ''; position: absolute; left: 4px; top: 1px; width: 4px; height: 8px;
  border: solid #fff; border-width: 0 2px 2px 0; transform: rotate(45deg);
}
.del-btn {
  position: absolute; top: 3px; right: 3px; width: 18px; height: 18px;
  border: none; border-radius: 50%; background: rgba(211,47,47,0.85); color: #fff;
  font-size: 0.8rem; line-height: 1; cursor: pointer; z-index: 2; padding: 0;
}
.del-btn:hover { background: #d32f2f; }
.frame-idx { position: absolute; bottom: 2px; right: 4px; background: rgba(0,0,0,0.6); color: #fff; font-size: 0.7rem; padding: 1px 4px; border-radius: 3px; }
.empty { text-align: center; padding: 3rem; color: #999; }
</style>
