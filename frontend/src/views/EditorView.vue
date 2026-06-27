<script setup>
import FrameList from '../components/FrameList.vue'
import FramePreview from '../components/FramePreview.vue'
import BatchToolbar from '../components/BatchToolbar.vue'
import FrameCanvas from '../components/FrameCanvas.vue'
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
        <FramePreview />
        <FrameCanvas />
      </section>
    </div>
  </div>
</template>

<style scoped>
h1 { margin-bottom: 1.5rem; color: #1a1a2e; }
.editor-layout { display: grid; grid-template-columns: 320px 1fr; gap: 1.5rem; }
.sidebar { overflow-y: auto; max-height: calc(100vh - 150px); }
.main-area { min-height: 500px; }
</style>
