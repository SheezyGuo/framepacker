const API_BASE = 'http://localhost:5080/api'

export async function extractFrames({ videoPath, fps = 12, output = './frames', start = 0, duration = null, resize = null }) {
  const params = { video_path: videoPath, fps, output, start }
  if (duration) params.duration = duration
  if (resize) params.resize = resize
  const res = await fetch(`${API_BASE}/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
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
