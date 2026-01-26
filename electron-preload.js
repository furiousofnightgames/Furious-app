const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  isDev: () => ipcRenderer.invoke('is-dev'),
  getAppVersion: () => '3.3.0',
  selectFolder: (path) => ipcRenderer.invoke('select-folder', path),
  getDefaultDownloadsPath: () => ipcRenderer.invoke('get-default-downloads-path'),

  // Window Controls
  minimizeWindow: () => ipcRenderer.send('window-minimize'),
  toggleMaximize: () => ipcRenderer.send('window-toggle-maximize'),
  closeWindow: () => ipcRenderer.send('window-close'),
  isMaximized: () => ipcRenderer.invoke('window-is-maximized'),
  onMaximizeChange: (callback) => ipcRenderer.on('window-maximize-change', callback),
  removeMaximizeListener: (callback) => ipcRenderer.removeListener('window-maximize-change', callback)
});
