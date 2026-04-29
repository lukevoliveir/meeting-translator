const { app, BrowserWindow, shell } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const http = require('http')

const isDev = process.env.NODE_ENV === 'development'
const BACKEND_PORT = 8000
const FRONTEND_PORT = 5173

let mainWindow = null
let backendProcess = null

// ── Backend ──────────────────────────────────────────────────────────────────

function getBackendExecutable() {
  const platform = process.platform // 'darwin' | 'win32' | 'linux'

  if (isDev) {
    // In dev, run Python source directly
    const python = platform === 'win32' ? 'python' : 'python3'
    return { cmd: python, args: ['main.py'], cwd: path.join(__dirname, '..', 'backend') }
  }

  // In production, use the PyInstaller binary bundled inside resources/
  const binName = platform === 'win32' ? 'backend.exe' : 'backend'
  const binPath = path.join(process.resourcesPath, 'backend-dist', binName)
  return { cmd: binPath, args: [], cwd: path.dirname(binPath) }
}

function startBackend() {
  const { cmd, args, cwd } = getBackendExecutable()
  console.log(`Starting backend: ${cmd} ${args.join(' ')}`)

  backendProcess = spawn(cmd, args, {
    cwd,
    stdio: ['ignore', 'pipe', 'pipe'],
    // Windows needs shell:true to find .exe from PATH
    shell: process.platform === 'win32',
  })

  backendProcess.stdout.on('data', (d) => process.stdout.write(`[backend] ${d}`))
  backendProcess.stderr.on('data', (d) => process.stderr.write(`[backend] ${d}`))
  backendProcess.on('exit', (code) => console.log(`Backend exited with code ${code}`))
}

function waitForBackend(retries = 30, delayMs = 500) {
  return new Promise((resolve, reject) => {
    const attempt = (n) => {
      const req = http.get(`http://localhost:${BACKEND_PORT}/health`, (res) => {
        if (res.statusCode === 200) return resolve()
        retry(n)
      })
      req.on('error', () => retry(n))
      req.setTimeout(500, () => { req.destroy(); retry(n) })
    }
    const retry = (n) => {
      if (n <= 0) return reject(new Error('Backend did not start in time'))
      setTimeout(() => attempt(n - 1), delayMs)
    }
    attempt(retries)
  })
}

function stopBackend() {
  if (!backendProcess) return
  console.log('Stopping backend...')
  if (process.platform === 'win32') {
    spawn('taskkill', ['/pid', backendProcess.pid.toString(), '/f', '/t'])
  } else {
    backendProcess.kill('SIGTERM')
  }
  backendProcess = null
}

// ── Window ────────────────────────────────────────────────────────────────────

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 700,
    minWidth: 800,
    minHeight: 560,
    title: 'Meeting Translator',
    backgroundColor: '#0f0f0f',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  // Open external links in the system browser, not inside Electron
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  if (isDev) {
    mainWindow.loadURL(`http://localhost:${FRONTEND_PORT}`)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'))
  }

  mainWindow.on('closed', () => { mainWindow = null })
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────

app.whenReady().then(async () => {
  startBackend()

  try {
    await waitForBackend()
    console.log('✓ Backend ready')
  } catch (err) {
    console.error('Backend failed to start:', err.message)
    // Show the window anyway — Prerequisites screen will display the error
  }

  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') app.quit()
})

app.on('before-quit', () => stopBackend())
