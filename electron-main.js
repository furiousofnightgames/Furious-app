const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const os = require('os');

const isDev = !app.isPackaged;

// PERFORMANCE: GPU acceleration strategy
// Keeping it simple to avoid driver crashes (exit_code=-1073740791) seen in logs
if (process.env.DISABLE_GPU === 'true' || isDev) {
  app.disableHardwareAcceleration();
  console.log('[PERF] GPU acceleration disabled (dev mode or env var)');
} else {
  // Use SAFE performance flags for smoother rendering in production
  app.commandLine.appendSwitch('enable-gpu-rasterization');
  app.commandLine.appendSwitch('enable-zero-copy');
  console.log('[PERF] GPU acceleration ENABLED (Safe Production Mode)');
}

let mainWindow;
let splashWindow;
let pythonProcess;
let backendReady = false;
let isQuitting = false; // Flag for graceful shutdown sequence

// Core variables

const ensureDirSync = (dirPath) => {
  try {
    fs.mkdirSync(dirPath, { recursive: true });
  } catch (e) {
  }
};

const safeRmSync = (p) => {
  try {
    if (fs.existsSync(p)) {
      fs.rmSync(p, { recursive: true, force: true });
    }
  } catch (e) {
  }
};

const dirSizeSync = (p) => {
  try {
    let total = 0;
    const stack = [p];
    while (stack.length) {
      const cur = stack.pop();
      let entries;
      try {
        entries = fs.readdirSync(cur, { withFileTypes: true });
      } catch (e) {
        continue;
      }
      for (const ent of entries) {
        const full = path.join(cur, ent.name);
        if (ent.isDirectory()) {
          stack.push(full);
        } else {
          try {
            total += fs.statSync(full).size;
          } catch (e) {
          }
        }
      }
    }
    return total;
  } catch (e) {
    return 0;
  }
};

const configureAppDataPaths = () => {
  try {
    const roamingRoot = app.getPath('appData');
    const localRoot = app.getPath('localAppData');

    const desiredUserData = path.join(roamingRoot, 'furiousapp');
    const desiredCache = path.join(localRoot, 'furiousapp', 'Cache');

    ensureDirSync(desiredUserData);
    ensureDirSync(desiredCache);

    app.setPath('userData', desiredUserData);
    app.setPath('cache', desiredCache);

    const maxCacheMb = Number(process.env.ELECTRON_CACHE_MAX_MB || 250);
    const maxBytes = Math.max(50, maxCacheMb) * 1024 * 1024;
    const cacheSize = dirSizeSync(desiredCache);
    if (cacheSize > maxBytes) {
      safeRmSync(desiredCache);
      ensureDirSync(desiredCache);
    }
  } catch (e) {
  }
};

configureAppDataPaths();

console.log('='.repeat(60));
console.log('FURIOUS APP - STARTUP');
console.log('='.repeat(60));
console.log('Mode:', isDev ? 'DEVELOPMENT' : 'PRODUCTION');
console.log('__dirname:', __dirname);
console.log('process.resourcesPath:', process.resourcesPath);
console.log('app.getAppPath():', app.getAppPath());
console.log('app.getPath(userData):', app.getPath('userData'));
console.log('app.getPath(cache):', app.getPath('cache'));

// Get correct base path for production vs development
const getBasePath = () => {
  if (isDev) {
    return __dirname;
  }
  // In production, app files are in resources/app
  return app.getAppPath();
};

const getBackendBasePath = () => {
  if (isDev) {
    return __dirname;
  }

  const appPath = app.getAppPath();
  if (typeof appPath === 'string' && appPath.endsWith('app.asar')) {
    return `${appPath}.unpacked`;
  }

  return appPath;
};

const moveFileIfMissingSync = (src, dst) => {
  try {
    if (fs.existsSync(src) && !fs.existsSync(dst)) {
      ensureDirSync(path.dirname(dst));
      try {
        fs.renameSync(src, dst);
      } catch (e) {
        try {
          fs.copyFileSync(src, dst);
          try {
            fs.unlinkSync(src);
          } catch (e2) {
          }
        } catch (e2) {
        }
      }
    }
  } catch (e) {
  }
};

const PYTHON_EXECUTABLE = isDev
  ? path.join(__dirname, 'portables', 'python-64bits', 'App', 'Python', 'python.exe')
  : path.join(process.resourcesPath, 'portables', 'python-64bits', 'App', 'Python', 'python.exe');
const BACKEND_PORT = 8001; // Changed from 8000 to avoid port conflicts
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;

console.log('Python executable path:', PYTHON_EXECUTABLE);
console.log('Python exists:', fs.existsSync(PYTHON_EXECUTABLE));
console.log('='.repeat(60));

function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 500,
    height: 300,
    frame: false,
    transparent: true, // RESTORED: Premium transparent look
    backgroundColor: '#050505', // SAFETY: Pre-fill background before HTML paints
    alwaysOnTop: true,
    show: false, // Don't show immediately to prevent the "white/black flash"
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'launcher', 'images', 'icone.ico')
  });

  splashWindow.center(); // Center first
  splashWindow.loadFile(path.join(__dirname, 'splash.html'));

  // Show only when fullly ready to ensure fluid appearance
  splashWindow.once('ready-to-show', () => {
    if (splashWindow && !splashWindow.isDestroyed()) {
      // 200ms buffer: Allows GPU composition to settle, preventing "Black Blink" on transparent windows
      setTimeout(() => {
        if (splashWindow && !splashWindow.isDestroyed()) {
          splashWindow.show();
        }
      }, 200);
    }
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1366,
    height: 768,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: '#0b1120', // Matches your cyberpunk dark bg
    show: false, // Wait for ready-to-show to prevent white flash
    frame: false, // Frameless window for custom title bar
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'electron-preload.js'),
      backgroundThrottling: false, // CRITICAL: Allows Enrichener to run while minimized
      sandbox: false, // Required for some advanced features
      spellcheck: false, // Disable spellcheck for perf
      webgl: true, // Enable WebGL for GPU-accelerated graphics
      enableWebSQL: false, // Disable deprecated WebSQL
      offscreen: false, // Use on-screen rendering for better performance
      experimentalFeatures: true // Enable experimental canvas features
    },
    icon: path.join(__dirname, 'launcher/images/icone.ico')
  });

  if (isDev) {
    const startUrl = 'http://localhost:5173';
    console.log('Loading Frontend (Dev):', startUrl);
    mainWindow.loadURL(startUrl);
    mainWindow.webContents.openDevTools();
  } else {
    // Production: Load from dist folder
    const basePath = getBasePath();
    const indexPath = path.join(basePath, 'frontend', 'dist', 'index.html');
    console.log('Loading Frontend (Prod):', indexPath);
    console.log('Base Path:', basePath);
    console.log('File exists:', fs.existsSync(indexPath));

    mainWindow.loadFile(indexPath).catch(err => {
      console.error('Failed to load local index.html:', err);
      // Fallback to backend if frontend build is missing (unlikely but safe)
      mainWindow.loadURL(BACKEND_URL);
    });
  }

  // Show window when ready to avoid flickering
  mainWindow.once('ready-to-show', () => {
    // Show main window first
    mainWindow.show();
    mainWindow.focus();

    // Small delay before destroying splash to ensure main window has painted
    setTimeout(() => {
      if (splashWindow && !splashWindow.isDestroyed()) {
        splashWindow.destroy();
        splashWindow = null;
      }
    }, 200);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // BLOCKING SHUTDOWN: Intercept close to ensure data is saved
  mainWindow.on('close', async (e) => {
    if (isQuitting) return; // Allow second call to proceed

    e.preventDefault(); // Stop window from closing immediately
    console.log('[SHUTDOWN] Window close intercepted. Starting cleanup...');

    // 1. Trigger Data Flush via API
    const http = require('http');
    try {
      console.log('[SHUTDOWN] Requesting mandatory metadata flush...');
      const request = http.get(`${BACKEND_URL}/api/system/flush`, (res) => {
        console.log('[SHUTDOWN] Flush request accepted by backend.');
        finishShutdown();
      });

      request.on('error', (err) => {
        console.log('[SHUTDOWN] Flush endpoint unreachable, proceeding to kill.');
        finishShutdown();
      });

      // Safety Timeout: Don't hang forever if backend is stuck
      setTimeout(() => {
        console.log('[SHUTDOWN] Flush timeout exceeded. Forcing exit.');
        finishShutdown();
      }, 2000);

    } catch (err) {
      finishShutdown();
    }
  });

  function finishShutdown() {
    if (isQuitting) return;
    isQuitting = true;
    console.log('[SHUTDOWN] Cleanup complete. Closing window.');
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.close();
    }
  }

  // Notify renderer about maximize state changes
  mainWindow.on('maximize', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('window-maximize-change', true);
    }
  });

  mainWindow.on('unmaximize', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('window-maximize-change', false);
    }
  });
}

function updateSplashStatus(percent, text) {
  if (splashWindow && !splashWindow.isDestroyed()) {
    splashWindow.webContents.send('progress', { percent, text });
  }
}

function startPythonBackend() {
  return new Promise((resolve) => {
    updateSplashStatus(10, 'Initializing Python Core...');

    // Check if executable exists
    if (!fs.existsSync(PYTHON_EXECUTABLE)) {
      console.error('Python executable not found at:', PYTHON_EXECUTABLE);
      updateSplashStatus(100, 'Python not found - continuing...');
      resolve();
      return;
    }

    const basePath = getBasePath();
    const backendBasePath = getBackendBasePath();
    const backendPath = path.join(backendBasePath, 'backend');
    const dataRoot = isDev ? basePath : app.getPath('userData');
    const logsDir = path.join(dataRoot, 'logs');
    const logPath = path.join(logsDir, 'backend.log');

    ensureDirSync(dataRoot);
    ensureDirSync(logsDir);

    // --- DATABASE SEED LOGIC: Import bundled Rich Metadata ---
    // Lógica: Só sobrescreve se for a PRIMEIRA vez desta versão (Instalação ou Update).
    // Isso garante que novos dados cheguem aos usuários sem resetar o progresso diário.
    const prodDbPath = path.join(dataRoot, 'data.db');
    const prodAppListPath = path.join(dataRoot, 'steam_applist.json');

    const bundledSeedRoot = isDev
      ? path.join(__dirname, 'data_seed')
      : path.join(process.resourcesPath, 'data_seed');

    const bundledDbPath = path.join(bundledSeedRoot, 'data.db');
    const bundledAppListPath = path.join(bundledSeedRoot, 'steam_applist.json');

    const versionFilePath = path.join(dataRoot, 'last_run_version.txt');
    const currentVersion = app.getVersion();

    try {
      const lastRunVersion = fs.existsSync(versionFilePath) ? fs.readFileSync(versionFilePath, 'utf8').trim() : '';

      if (lastRunVersion !== currentVersion) {
        console.log(`[DB] Nova instalação ou atualização detectada (${currentVersion})`);

        if (fs.existsSync(bundledDbPath)) {
          // PROTECTION: Only copy if the file DOES NOT exist
          if (!fs.existsSync(prodDbPath)) {
            console.log('[DB] Pasta vazia. Instalando banco rico inicial...');
            fs.copyFileSync(bundledDbPath, prodDbPath);
            console.log('[DB] Banco rico semeado com sucesso.');
          } else {
            console.log('[DB] Banco local já existe. Preservando seu progresso e ignorando semente.');
          }

          if (fs.existsSync(bundledAppListPath) && !fs.existsSync(prodAppListPath)) {
            fs.copyFileSync(bundledAppListPath, prodAppListPath);
            console.log('[DB] steam_applist.json semeado.');
          }
        }

        // Salva a versão atual como "última rodada"
        fs.writeFileSync(versionFilePath, currentVersion, 'utf8');
      } else {
        console.log('[DB] Versão idêntica à última execução. Preservando banco local.');
      }
    } catch (dbErr) {
      console.error('[DB] Erro na semente de dados:', dbErr.message);
    }

    if (dataRoot !== basePath) {
      // Outros arquivos de sessão (Não copiamos steam_applist.json pois o banco rico já resolve isso)
      moveFileIfMissingSync(path.join(basePath, 'aria2.session'), path.join(dataRoot, 'aria2.session'));
      moveFileIfMissingSync(path.join(basePath, 'dht.dat'), path.join(dataRoot, 'dht.dat'));
    }

    console.log('Python executable:', PYTHON_EXECUTABLE);
    console.log('Backend path:', backendPath);
    console.log('Working directory:', backendBasePath);
    console.log('Log file:', logPath);

    // Create log file stream (overwrite on each session)
    const logStream = fs.createWriteStream(logPath, { flags: 'w' });
    logStream.write(`[SESSION START] ${new Date().toISOString()}\n`);
    logStream.write('='.repeat(80) + '\n\n');

    const pythonArgs = isDev
      ? ['-m', 'uvicorn', 'backend.main:app', '--reload', '--host', '127.0.0.1', '--port', String(BACKEND_PORT)]
      : ['-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', String(BACKEND_PORT)];

    // Calculate Aria2 path (Critical)
    const ARIA2_PATH = isDev
      ? path.join(__dirname, 'portables', 'aria2-1.37.0', 'aria2c.exe')
      : path.join(process.resourcesPath, 'portables', 'aria2-1.37.0', 'aria2c.exe');

    let options = {
      cwd: backendBasePath, // Use unpacked base path as working directory when packaged
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true, // Hide console window
      env: {
        ...process.env,
        PYTHONIOENCODING: 'utf-8',
        ARIA2C_PATH: ARIA2_PATH,
        APP_DATA_DIR: dataRoot,
        DB_PATH: path.join(dataRoot, 'data.db'),
        STEAM_APP_LIST_FILE: path.join(dataRoot, 'steam_applist.json'),
        ARIA2_SESSION_FILE: path.join(dataRoot, 'aria2.session'),
        ARIA2_DHT_FILE: path.join(dataRoot, 'dht.dat')
      }
    };

    try {
      updateSplashStatus(30, 'Starting Backend Services...');
      pythonProcess = spawn(PYTHON_EXECUTABLE, pythonArgs, options);

      pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        logStream.write(output);
        console.log(`[Python] ${output}`);
        if (output.includes('Application startup complete')) {
          updateSplashStatus(100, 'System Ready.');
          backendReady = true;
          resolve();
        }
      });

      pythonProcess.stderr.on('data', (data) => {
        const error = data.toString();
        logStream.write(error);
        // Filter noise
        if (!error.toLowerCase().includes('info:') && !error.toLowerCase().includes('warning')) {
          console.error(`[Python Error] ${error}`);
        }
        // Also resolve on Uvicorn startup (sometimes output goes to stderr)
        if (error.includes('Application startup complete') || error.includes('Uvicorn running on')) {
          updateSplashStatus(100, 'System Ready.');
          backendReady = true;
          resolve();
        }
      });

      pythonProcess.on('error', (err) => {
        console.error('Failed to start Python process:', err);
        logStream.write(`[ERROR] Failed to start: ${err.message}\n`);
        logStream.end();
        resolve();
      });

      pythonProcess.on('exit', (code) => {
        console.log(`Python process exited with code ${code}`);
        logStream.write(`[EXIT] Process exited with code ${code}\n`);
        logStream.end();
      });

      // Auto-resolve after a timeout if no signal received
      setTimeout(() => {
        if (!backendReady) {
          console.log('Backend timeout, proceeding...');
          logStream.write('[TIMEOUT] Backend startup timeout, proceeding anyway\n');
          resolve();
        }
      }, 8000); // 8 seconds timeout for splash

    } catch (e) {
      console.error('Failed to spawn python:', e);
      logStream.write(`[EXCEPTION] ${e.message}\n`);
      logStream.end();
      resolve();
    }
  });
}

function createMenu() {
  Menu.setApplicationMenu(null); // Hide default menu for modern look
}

app.on('ready', async () => {
  createSplashWindow();
  createMenu();

  // Artificial delay for splash effect if backend is too fast
  const startTime = Date.now();

  try {
    await startPythonBackend();
  } catch (e) {
    console.error(e);
  }

  const elapsed = Date.now() - startTime;
  const minSplashTime = 5000; // Minimum 5s splash for consistent "loading" feel
  if (elapsed < minSplashTime) {
    setTimeout(createWindow, minSplashTime - elapsed);
  } else {
    createWindow();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
  if (pythonProcess) {
    console.log('[SHUTDOWN] Final termination of Python backend...');
    if (process.platform === 'win32') {
      exec(`taskkill /pid ${pythonProcess.pid} /T`);
    } else {
      pythonProcess.kill('SIGTERM');
    }
  }
});

ipcMain.handle('get-backend-url', () => BACKEND_URL);
ipcMain.handle('is-dev', () => isDev);

const { dialog } = require('electron');
ipcMain.handle('select-folder', async (event, startPath) => {
  if (!mainWindow) return null;

  let defaultPath = undefined;
  try {
    defaultPath = startPath || app.getPath('downloads');
  } catch (e) { }

  const result = await dialog.showOpenDialog(mainWindow, {
    defaultPath: defaultPath,
    properties: ['openDirectory', 'createDirectory', 'promptToCreate']
  });
  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }
  return result.filePaths[0];
});

ipcMain.handle('get-default-downloads-path', () => {
  try {
    return app.getPath('downloads');
  } catch (e) {
    return null;
  }
});

// Window Controls IPC Handlers
ipcMain.on('window-minimize', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.minimize();
  }
});

ipcMain.on('window-toggle-maximize', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

ipcMain.on('window-close', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.close();
  }
});

ipcMain.handle('window-is-maximized', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    return mainWindow.isMaximized();
  }
  return false;
});
