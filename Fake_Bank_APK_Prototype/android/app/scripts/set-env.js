// scripts/set-env.js
const fs = require('fs');
const path = require('path');

const environment = process.argv[2] || 'development';
const envFile = path.resolve(__dirname, `../.env.${environment}`);

if (fs.existsSync(envFile)) {
  console.log(`Using ${environment} environment`);
} else {
  console.error(`Environment file not found: ${envFile}`);
  process.exit(1);
}