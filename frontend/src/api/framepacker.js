const API_BASE = '/api'

export function frameUrl(path) {
  return `${API_BASE}/file?path=${encodeURIComponent(path)}`
}

export async function cleanupWorkspace() {
  const res = await fetch(`${API_BASE}/cleanup`, {
    method: 'POST',
  })
  if (!res.ok) throw new Error(`Cleanup failed: ${res.statusText}`)
  return res.json()
}

export async function extractFrames({ videoFile, fps = 12, start = 0, duration = null, resize = null }) {
  const form = new FormData()
  form.append('file', videoFile)
  form.append('fps', fps)
  form.append('start', start)
  if (duration) form.append('duration', duration)
  if (resize) form.append('resize', resize)
  const res = await fetch(`${API_BASE}/extract`, {
    method: 'POST',
    body: form,
  })
  if (!res.ok) throw new Error(`Extract failed: ${res.statusText}`)
  return res.json()
}

export async function framesToGif({ framesDir, fps = 10, output = 'output.gif', resize = null, loop = 0 }) {
  const params = { frames_dir: framesDir, fps, output, loop }
  if (resize) params.resize = resize
  const res = await fetch(`${API_BASE}/gif`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`GIF failed: ${res.statusText}`)
  return res.json()
}

export async function framesToSprite({ framesDir, cols = 8, output = 'sprite.png', padding = 2, resize = null }) {
  const params = { frames_dir: framesDir, cols, output, padding }
  if (resize) params.resize = resize
  const res = await fetch(`${API_BASE}/sprite`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Sprite failed: ${res.statusText}`)
  return res.json()
}

export async function dedupFrames({ framesDir, threshold = 0.92, output = null }) {
  const params = { frames_dir: framesDir, threshold }
  if (output) params.output = output
  const res = await fetch(`${API_BASE}/dedup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Dedup failed: ${res.statusText}`)
  return res.json()
}

export async function detectDupes({ framesDir, threshold = 0.92 }) {
  const res = await fetch(`${API_BASE}/detect-dupes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ frames_dir: framesDir, threshold }),
  })
  if (!res.ok) throw new Error(`Detect dupes failed: ${res.statusText}`)
  return res.json()
}

export async function detectJumps({ framesDir, threshold = 0.4 }) {
  const res = await fetch(`${API_BASE}/detect-jumps`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ frames_dir: framesDir, threshold }),
  })
  if (!res.ok) throw new Error(`Detect jumps failed: ${res.statusText}`)
  return res.json()
}

export async function exportZip({ framesDir, name = 'frames.zip' }) {
  const res = await fetch(`${API_BASE}/export-zip`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ frames_dir: framesDir, name }),
  })
  if (!res.ok) throw new Error(`Export zip failed: ${res.statusText}`)
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = name
  a.click()
  URL.revokeObjectURL(url)
}

export async function importGif(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_BASE}/import-gif`, {
    method: 'POST',
    body: form,
  })
  if (!res.ok) throw new Error(`Import gif failed: ${res.statusText}`)
  return res.json()
}

export async function saveFrame({ path, data }) {
  const res = await fetch(`${API_BASE}/save-frame`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, data }),
  })
  if (!res.ok) throw new Error(`Save frame failed: ${res.statusText}`)
  return res.json()
}

export async function removeBg({ framesDir, output = null }) {
  const params = { frames_dir: framesDir }
  if (output) params.output = output
  const res = await fetch(`${API_BASE}/remove-bg`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Remove-BG failed: ${res.statusText}`)
  return res.json()
}

export async function batchEdit({ framesDir, resize = null, crop = null, rotate = null, grayscale = false, output = null }) {
  const params = { frames_dir: framesDir, grayscale }
  if (resize) params.resize = resize
  if (crop) params.crop = crop
  if (rotate !== null) params.rotate = rotate
  if (output) params.output = output
  const res = await fetch(`${API_BASE}/edit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Edit failed: ${res.statusText}`)
  return res.json()
}
