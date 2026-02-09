const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let win;
let isExpanded = false;
let backendProcess;
let backendStartTime = 0;
const COLLAPSED_SIZE = { width: 80, height: 140 };
const EXPANDED_SIZE = { width: 760, height: 700 };
let dragOffset = null;

function attachProcessLogs(proc, label) {
    if (!proc || !proc.stdout || !proc.stderr) return;
    proc.stdout.on('data', (data) => console.log(`[backend:${label}] ${data}`));
    proc.stderr.on('data', (data) => console.error(`[backend:${label}] ${data}`));
}

function startBackend() {
    if (backendProcess) return;
    backendStartTime = Date.now();
    const repoRoot = path.join(__dirname, '..');
    const args = [
        '-m', 'uvicorn', 'api_server:app',
        '--host', '127.0.0.1', '--port', '8000',
        '--reload'
    ];
    const pyCommand = 'py -3.13';
    backendProcess = spawn(pyCommand, args, { cwd: repoRoot, stdio: 'pipe', shell: true });
    attachProcessLogs(backendProcess, 'py-3.13');
    backendProcess.on('exit', (code) => {
        console.error(`[backend] py -3.13 exited with code ${code}`);
    });
}

function stopBackend() {
    if (!backendProcess) return;
    backendProcess.kill();
    backendProcess = null;
}

function createWindow() {
    win = new BrowserWindow({
        width: COLLAPSED_SIZE.width,
        height: COLLAPSED_SIZE.height,
        frame: false,
        transparent: true,
        // backgroundColor: '#ffffff',
        alwaysOnTop: true,
        resizable: false,
        movable: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    win.loadFile('index.html');
    
    // 生产模式不自动打开 DevTools
    
    console.log('✅ 窗口创建成功');
    applyWindowSize(false);
    win.setAlwaysOnTop(true);

    // Hard lock window size in case of any external resize.
    win.on('will-resize', (e) => {
        e.preventDefault();
        applyWindowSize(isExpanded);
    });
    win.on('resize', () => {
        applyWindowSize(isExpanded);
    });
}

// 展开/收起

function applyWindowSize(expanded, position) {
    const target = expanded ? EXPANDED_SIZE : COLLAPSED_SIZE;
    const [x, y] = position || win.getPosition();
    const currentHeight = win.getBounds().height;
    const deltaY = target.height - currentHeight;
    win.setBounds({
        x: x,
        y: y - deltaY, // 只在 Y 方向调整，保持底部对齐
        width: target.width,
        height: target.height
    });
    win.setMinimumSize(target.width, target.height);
    win.setMaximumSize(target.width, target.height);
}

ipcMain.on('toggle', () => {
    isExpanded = !isExpanded;
    // Only keep top-most when collapsed as icon
    win.setAlwaysOnTop(!isExpanded);
    if (isExpanded) {
        win.setIgnoreMouseEvents(true, { forward: true });
    } else {
        win.setIgnoreMouseEvents(false);
    }
    applyWindowSize(isExpanded);
    win.webContents.send('state', isExpanded);
});

ipcMain.on('set-pass-through', (event, enabled) => {
    if (isExpanded) {
        win.setIgnoreMouseEvents(!!enabled, { forward: true });
    }
});

ipcMain.on('app-quit', () => {
    app.quit();
});

// 移动窗口
ipcMain.on('drag-start', (event, { screenX, screenY }) => {
    const [x, y] = win.getPosition();
    dragOffset = { x: screenX - x, y: screenY - y };
});

ipcMain.on('drag-move', (event, { screenX, screenY }) => {
    if (!dragOffset) return;
    win.setPosition(screenX - dragOffset.x, screenY - dragOffset.y, false);
});

ipcMain.on('drag-end', () => {
    dragOffset = null;
});

// Ignore any renderer resize requests to keep strict sizes.
ipcMain.on('resize-window', () => {
    applyWindowSize(isExpanded);
});

app.whenReady().then(() => {
    startBackend();
    createWindow();
});
app.on('before-quit', stopBackend);
app.on('window-all-closed', () => app.quit());

