const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  isDev: () => ipcRenderer.invoke('is-dev'),
  getAppVersion: () => '1.0.0',
  selectFolder: () => ipcRenderer.invoke('select-folder')
});
