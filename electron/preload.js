const { contextBridge, ipcRenderer } = require('electron')

// Expose a minimal API to the renderer — nothing sensitive
contextBridge.exposeInMainWorld('electronAPI', {
  platform: () => process.platform,
})
