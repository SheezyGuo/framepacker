<script setup>
import VideoUpload from '../components/VideoUpload.vue'
import FrameExtractor from '../components/FrameExtractor.vue'
import GifImport from '../components/GifImport.vue'
</script>

<template>
  <div class="extract-view">
    <h1>视频抽帧</h1>
    <VideoUpload />
    <FrameExtractor />
    <GifImport />
  </div>
</template>

<style scoped>
h1 { margin-bottom: 1.5rem; color: #1a1a2e; }
</style>
