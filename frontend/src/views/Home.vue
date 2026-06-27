<script setup>
</script>

<template>
  <div class="home">
    <section class="hero">
      <h1>FramePacker Local</h1>
      <p class="subtitle">视频转序列帧 / GIF / 帧动画 — 完全离线</p>
      <div class="actions">
        <router-link to="/extract" class="btn-primary">开始提取帧</router-link>
      </div>
    </section>

    <section class="features">
      <div class="card">
        <h3>📹 视频抽帧</h3>
        <p>上传视频，选好帧率和时长，一键提取帧画面</p>
      </div>
      <div class="card">
        <h3>✏️ 帧编辑器</h3>
        <p>逐帧预览、排序去重、批量抠图、换背景</p>
      </div>
      <div class="card">
        <h3>🎞️ 导出</h3>
        <p>GIF 动图 / PNG 序列帧 / 精灵表，自定义分辨率</p>
      </div>
      <div class="card">
        <h3>⚡ 自动化流水线</h3>
        <p>YAML 配置多步处理，CLI 脚本一键执行</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero { text-align: center; padding: 4rem 0; }
.hero h1 { font-size: 3rem; color: #1a1a2e; }
.subtitle { font-size: 1.2rem; color: #666; margin: 1rem 0 2rem; }
.btn-primary { display: inline-block; padding: 0.8rem 2rem; background: #ff6b35; color: #fff; text-decoration: none; border-radius: 8px; font-weight: 600; }
.features { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
.card { background: #fff; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.card h3 { margin-bottom: 0.5rem; color: #1a1a2e; }
.card p { color: #555; line-height: 1.6; }
</style>
