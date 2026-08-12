<script setup>
import FrameList from '../components/FrameList.vue'
import FramePreview from '../components/FramePreview.vue'
import BatchToolbar from '../components/BatchToolbar.vue'
import FrameCanvas from '../components/FrameCanvas.vue'
import AnimationPreview from '../components/AnimationPreview.vue'
</script>

<template>
  <div class="editor-view">
    <h1>帧编辑器</h1>
    <div class="editor-layout">
      <aside class="sidebar">
        <BatchToolbar />
        <FrameList />
      </aside>
      <section class="main-area">
        <div class="preview-row">
          <FramePreview />
          <AnimationPreview />
        </div>
        <FrameCanvas />
      </section>
    </div>
  </div>
</template>

<style scoped>
h1 { margin-bottom: 1.5rem; color: #1a1a2e; }
.editor-layout { display: grid; grid-template-columns: 480px 1fr; gap: 1.5rem; }
.sidebar { overflow-y: auto; max-height: calc(100vh - 150px); }
.main-area { min-height: 500px; }

.preview-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.preview-row > * { min-width: 0; }

:deep(.panel) {
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 1rem;
}

@media (max-width: 900px) {
  .preview-row { grid-template-columns: 1fr; }
}
</style>
