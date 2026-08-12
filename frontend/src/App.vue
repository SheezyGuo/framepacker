<script setup>
</script>

<template>
  <div id="app-root">
    <header>
      <nav>
        <router-link to="/">FramePacker</router-link>
        <router-link to="/extract">提取帧</router-link>
        <router-link to="/editor">帧编辑器</router-link>
        <router-link to="/export">导出</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: sans-serif; background: #f5f5f5; color: #333; }
header { background: #1a1a2e; padding: 1rem 2rem; }
nav { display: flex; gap: 1.5rem; align-items: center; }
nav a { color: #e0e0e0; text-decoration: none; font-weight: 500; }
nav a:hover { color: #fff; }
nav a:first-child { font-size: 1.2rem; font-weight: 700; color: #ff6b35; }
main { max-width: 1600px; margin: 0 auto; padding: 2rem; }
</style>
