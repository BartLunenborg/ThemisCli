// setup.js
const fs = require('fs-extra');
const path = require('path');
const os = require('os');

const configDir = path.join(os.homedir(), '.config', 'themis_cli');
const configPath = path.join(configDir, 'config.json');

const defaultConfig = {
  user: "",
  year: "2024-2025"
};

fs.ensureDirSync(configDir);

if (!fs.existsSync(configPath)) {
  fs.writeJsonSync(configPath, defaultConfig, { spaces: 2 });
  console.log('Default config file created at', configPath);
} else {
  console.log('Config file already exists at', configPath);
}
