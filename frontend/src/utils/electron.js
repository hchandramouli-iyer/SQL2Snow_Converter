// Utility functions for Electron integration

export const isElectron = () => {
  // Check if running in Electron
  return !!(
    typeof window !== 'undefined' &&
    window.process &&
    window.process.type === 'renderer'
  ) || !!(
    typeof process !== 'undefined' &&
    process.versions &&
    process.versions.electron
  ) || !!(
    typeof navigator === 'object' &&
    typeof navigator.userAgent === 'string' &&
    navigator.userAgent.indexOf('Electron') >= 0
  );
};

export const getElectronAPI = () => {
  if (isElectron() && window.require) {
    return window.require('electron');
  }
  return null;
};

export const showSaveDialog = async (options = {}) => {
  const electron = getElectronAPI();
  if (electron) {
    const { dialog } = electron.remote || electron;
    return await dialog.showSaveDialog(options);
  }
  return null;
};

export const showOpenDialog = async (options = {}) => {
  const electron = getElectronAPI();
  if (electron) {
    const { dialog } = electron.remote || electron;
    return await dialog.showOpenDialog(options);
  }
  return null;
};

export const openExternal = (url) => {
  const electron = getElectronAPI();
  if (electron) {
    const { shell } = electron;
    shell.openExternal(url);
  } else {
    // Fallback for web version
    window.open(url, '_blank');
  }
};

// Listen for Electron menu events
export const setupElectronListeners = (callbacks = {}) => {
  if (!isElectron()) return;
  
  const { ipcRenderer } = window.require('electron');
  
  if (callbacks.onNewProject) {
    ipcRenderer.on('new-project', callbacks.onNewProject);
  }
  
  if (callbacks.onOpenFile) {
    ipcRenderer.on('open-file', callbacks.onOpenFile);
  }
  
  if (callbacks.onSaveFile) {
    ipcRenderer.on('save-file', callbacks.onSaveFile);
  }
  
  if (callbacks.onSwitchTool) {
    ipcRenderer.on('switch-tool', callbacks.onSwitchTool);
  }
  
  // Return cleanup function
  return () => {
    ipcRenderer.removeAllListeners('new-project');
    ipcRenderer.removeAllListeners('open-file'); 
    ipcRenderer.removeAllListeners('save-file');
    ipcRenderer.removeAllListeners('switch-tool');
  };
};

// File system operations for Electron
export const readFileContent = async (filePath) => {
  if (!isElectron()) return null;
  
  const fs = window.require('fs');
  return new Promise((resolve, reject) => {
    fs.readFile(filePath, 'utf8', (err, data) => {
      if (err) reject(err);
      else resolve(data);
    });
  });
};

export const writeFileContent = async (filePath, content) => {
  if (!isElectron()) return false;
  
  const fs = window.require('fs');
  return new Promise((resolve, reject) => {
    fs.writeFile(filePath, content, 'utf8', (err) => {
      if (err) reject(err);
      else resolve(true);
    });
  });
};