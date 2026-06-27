import { defineStore } from 'pinia'

export const useFrameStore = defineStore('frames', {
  state: () => ({
    videoFile: null,
    frames: [],
    fps: 12,
    selectedFrames: new Set(),
  }),
  getters: {
    frameCount: (state) => state.frames.length,
    selectedCount: (state) => state.selectedFrames.size,
  },
  actions: {
    setVideo(file) { this.videoFile = file; },
    addFrames(paths) { this.frames.push(...paths); },
    clearFrames() { this.frames = []; this.selectedFrames.clear(); },
    toggleSelect(idx) {
      if (this.selectedFrames.has(idx)) this.selectedFrames.delete(idx)
      else this.selectedFrames.add(idx)
    },
    selectAll() {
      this.selectedFrames = new Set(this.frames.map((_, i) => i))
    },
    deselectAll() { this.selectedFrames.clear(); },
    removeSelected() {
      const sorted = [...this.selectedFrames].sort((a, b) => b - a)
      for (const idx of sorted) this.frames.splice(idx, 1)
      this.selectedFrames.clear()
    },
    removeFrame(idx) { this.frames.splice(idx, 1); },
    moveFrame(from, to) {
      const [item] = this.frames.splice(from, 1)
      this.frames.splice(to, 0, item)
    },
  },
})
