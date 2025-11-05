// Simple test to verify Electron is working
const { app, BrowserWindow } = require('electron');

console.log('Electron app object:', app ? 'EXISTS' : 'UNDEFINED');
console.log('Electron version:', process.versions.electron);

if (app) {
  app.whenReady().then(() => {
    console.log('Electron is ready!');
    const win = new BrowserWindow({
      width: 800,
      height: 600
    });
    win.loadURL('data:text/html,<h1>Electron Works!</h1>');

    setTimeout(() => {
      console.log('Test complete');
      app.quit();
    }, 2000);
  });
} else {
  console.error('ERROR: app is undefined!');
  process.exit(1);
}
