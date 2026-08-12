<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useFrameStore } from '../stores/frames'
import { frameUrl } from '../api/framepacker'

const store = useFrameStore()
const playing = ref(false)
const fps = ref(10)
const idx = ref(0)
let timer = null

const playFrames = computed(() => {
  return store.frames
    .map((path, i) => ({ path, origIdx: i }))
    .filter((f) => store.selectedFrames.has(f.origIdx))
})

const currentFrame = computed(() => {
  if (!playFrames.value.length) return null
  return playFrames.value[idx.value]
})

watch(() => playFrames.value.length, (n) => {
  if (n < 2) pause()
  if (idx.value >= n) idx.value = 0
})

function play() {
  if (playFrames.value.length < 2) return
  playing.value = true
  timer = setInterval(() => {
    idx.value = (idx.value + 1) % playFrames.value.length
  }, 1000 / fps.value)
}

function pause() {
  playing.value = false
  clearInterval(timer)
  timer = null
}

function toggle() {
  playing.value ? pause() : play()
}

function step(dir) {
  pause()
  if (!playFrames.value.length) return
  idx.value = (idx.value + dir + playFrames.value.length) % playFrames.value.length
}

function restart() {
  pause()
  idx.value = 0
  play()
}

function applyFps() {
  if (!fps.value || fps.value < 1) fps.value = 1
  if (fps.value > 120) fps.value = 120
  if (playing.value) {
    pause()
    play()
  }
}

onUnmounted(pause)
</script>

<template>
  <div class="panel anim-preview">
    <h2>动画预览</h2>
    <div v-if="currentFrame" class="anim-stage-wrap">
      <div class="anim-stage">
        <img :src="frameUrl(currentFrame.path)" alt="animation preview" />
        <span class="frame-badge">第 {{ currentFrame.origIdx + 1 }} 帧 / 选中 {{ playFrames.length }} 帧</span>
      </div>
    </div>
    <div v-else class="anim-empty"><p>暂无帧数据</p></div>

    <div class="anim-controls" v-if="store.frames.length">
      <button @click="step(-1)">上一帧</button>
      <button class="play-btn" @click="toggle" :disabled="playFrames.length < 2">{{ playing ? '暂停' : '播放' }}</button>
      <button @click="step(1)">下一帧</button>
      <button @click="restart" :disabled="playFrames.length < 2">重播</button>
      <label class="fps-control">
        速度
        <input v-model.number="fps" type="range" min="1" max="120" @input="applyFps" />
        <input v-model.number="fps" type="number" min="1" max="120" @change="applyFps" />
        fps
      </label>
    </div>
    <p class="hint" v-if="store.frames.length && playFrames.length < 2">提示：请在左侧选中至少 2 帧后播放预览，未选中的帧不会参与播放</p>
    <p class="hint" v-else>提示：播放效果即 GIF 导出的最终动画效果，建议先用此功能预览后再导出</p>
  </div>
</template>

<style scoped>
.anim-preview { display: flex; flex-direction: column; }
.anim-preview h2 { font-size: 1rem; color: #1a1a2e; margin-bottom: 0.75rem; text-align: left; }
.anim-stage-wrap { flex: 1; display: flex; align-items: center; justify-content: center; min-height: 240px; }
.anim-stage { position: relative; }
.anim-stage img { max-width: 100%; max-height: 300px; border: 1px solid #ddd; border-radius: 8px; background: #fff; }
.frame-badge { position: absolute; bottom: 6px; right: 8px; background: rgba(0,0,0,0.65); color: #fff; font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; }
.anim-controls { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap; }
.anim-controls button { padding: 0.3rem 0.8rem; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; }
.anim-controls button:hover:not(:disabled) { border-color: #ff6b35; }
.anim-controls button:disabled { opacity: 0.4; cursor: not-allowed; }
.play-btn { background: #ff6b35 !important; color: #fff; border-color: #ff6b35 !important; }
.anim-controls label { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; color: #555; }
.anim-controls input[type="range"] { width: 100px; }
.fps-control input[type="number"] { width: 56px; padding: 0.25rem 0.4rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem; }
.anim-empty { text-align: center; padding: 2rem; color: #999; border: 1px dashed #ddd; border-radius: 8px; }
.hint { font-size: 0.8rem; color: #999; margin-top: 0.5rem; }
</style>
