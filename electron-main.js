const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const os = require('os');

// Disable hardware acceleration
app.disableHardwareAcceleration();

let mainWindow;
let splashWindow;
let pythonProcess;
let backendReady = false;

// Custom isDev detection (app.isPackaged is false in development)
const isDev = !app.isPackaged;

console.log('='.repeat(60));
console.log('FURIOUS APP - STARTUP');
console.log('='.repeat(60));
console.log('Mode:', isDev ? 'DEVELOPMENT' : 'PRODUCTION');
console.log('__dirname:', __dirname);
console.log('process.resourcesPath:', process.resourcesPath);
console.log('app.getAppPath():', app.getAppPath());

// Get correct base path for production vs development
const getBasePath = () => {
  if (isDev) {
    return __dirname;
  }
  // In production, app files are in resources/app
  return app.getAppPath();
};

const ensureDirSync = (dirPath) => {
  try {
    fs.mkdirSync(dirPath, { recursive: true });
  } catch (e) {
  }
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
    transparent: true,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false // Allowed for simple local splash
    },
    icon: path.join(__dirname, 'launcher', 'images', 'icone.ico')
  });

  splashWindow.loadFile(path.join(__dirname, 'splash.html'));
  splashWindow.center();
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    show: false, // Wait until ready to show
    webPreferences: {
      preload: path.join(__dirname, 'electron-preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true
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
    if (splashWindow) {
      splashWindow.destroy();
      splashWindow = null;
    }
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
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
    const backendPath = path.join(basePath, 'backend');
    const dataRoot = isDev ? basePath : app.getPath('userData');
    const logsDir = path.join(dataRoot, 'logs');
    const logPath = path.join(logsDir, 'backend.log');

    ensureDirSync(dataRoot);
    ensureDirSync(logsDir);

    if (dataRoot !== basePath) {
      moveFileIfMissingSync(path.join(basePath, 'data.db'), path.join(dataRoot, 'data.db'));
      moveFileIfMissingSync(path.join(basePath, 'steam_applist.json'), path.join(dataRoot, 'steam_applist.json'));
      moveFileIfMissingSync(path.join(basePath, 'aria2.session'), path.join(dataRoot, 'aria2.session'));
      moveFileIfMissingSync(path.join(basePath, 'dht.dat'), path.join(dataRoot, 'dht.dat'));
    }

    console.log('Python executable:', PYTHON_EXECUTABLE);
    console.log('Backend path:', backendPath);
    console.log('Working directory:', basePath);
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
      cwd: basePath, // Use base path as working directory
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true, // Hide console window
      env: {
        ...process.env,
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
  const minSplashTime = 2000; // Minimum 2s splash
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
  if (pythonProcess) {
    console.log('Terminating Python backend...');
    // Robust kill on Windows
    if (process.platform === 'win32') {
      exec(`taskkill /pid ${pythonProcess.pid} /T /F`, (err) => {
        if (err) console.log('Taskkill error (process might be dead):', err.message);
      });
    } else {
      pythonProcess.kill();
    }
  }
});

ipcMain.handle('get-backend-url', () => BACKEND_URL);
ipcMain.handle('is-dev', () => isDev);

const { dialog } = require('electron');
ipcMain.handle('select-folder', async () => {
  if (!mainWindow) return null;
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'createDirectory', 'promptToCreate']
  });
  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }
  return result.filePaths[0];
});
