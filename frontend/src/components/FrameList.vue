<script setup>
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()

function onDragStart(e, idx) {
  e.dataTransfer.setData('text/plain', idx)
}
function onDrop(e, idx) {
  const from = parseInt(e.dataTransfer.getData('text/plain'))
  if (from !== idx) store.moveFrame(from, idx)
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
        @click="store.toggleSelect(idx)">
        <img :src="frame" :alt="'Frame ' + idx" />
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
.frame-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 0.5rem; }
.frame-thumb { position: relative; border: 2px solid transparent; border-radius: 6px; cursor: pointer; transition: border-color 0.2s; }
.frame-thumb:hover { border-color: #ff6b35; }
.frame-thumb.selected { border-color: #1a1a2e; background: #e0e0e0; }
.frame-thumb img { width: 100%; height: 80px; object-fit: cover; border-radius: 4px; }
.frame-idx { position: absolute; bottom: 2px; right: 4px; background: rgba(0,0,0,0.6); color: #fff; font-size: 0.7rem; padding: 1px 4px; border-radius: 3px; }
.empty { text-align: center; padding: 3rem; color: #999; }
</style>
