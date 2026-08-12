const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const serve = require('electron-serve');
const http = require('http');

const loadURL = serve({ directory: path.join(__dirname, 'frontend', 'out') });
let backendProcess;
let mainWindow;

function checkBackendReady(port, callback) {
  const req = http.get(`http://127.0.0.1:${port}/api/health`, (res) => {
    if (res.statusCode === 200) {
      callback(true);
    } else {
      setTimeout(() => checkBackendReady(port, callback), 500);
    }
  });
  
  req.on('error', () => {
    setTimeout(() => checkBackendReady(port, callback), 500);
  });
}

function startBackend() {
  const backendPath = path.join(__dirname, 'backend-dist', 'optitole-backend.exe');

  console.log("Starting backend:", backendPath);
  
  // Start the backend on a fixed port (e.g., 8000)
  backendProcess = spawn(backendPath, []);
  
  backendProcess.stdout.on('data', (data) => console.log(`backend: ${data}`));
  backendProcess.stderr.on('data', (data) => console.error(`backend: ${data}`));
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  if (app.isPackaged) {
    // In production, we serve the static files with electron-serve
    loadURL(mainWindow);
  } else {
    // In development, Next.js server runs on port 3000
    mainWindow.loadURL('http://localhost:3000');
  }
}

app.whenReady().then(() => {
  if (app.isPackaged) {
    startBackend();
    // Wait for the backend to start up
    checkBackendReady(8000, () => {
      console.log("Backend is ready!");
      createWindow();
    });
  } else {
    // In dev, assume backend and frontend are already running manually
    createWindow();
  }
});

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});
