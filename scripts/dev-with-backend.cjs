const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const root = process.cwd();
const isWin = process.platform === 'win32';

const npmCmd = isWin ? 'npm.cmd' : 'npm';
const nextCmd = isWin
  ? path.join(root, 'node_modules', '.bin', 'next.cmd')
  : path.join(root, 'node_modules', '.bin', 'next');
const pythonVenvPath = isWin
  ? path.join(root, '.venv', 'Scripts', 'python.exe')
  : path.join(root, '.venv', 'bin', 'python');

const pythonCmd = fs.existsSync(pythonVenvPath) ? pythonVenvPath : 'python';

const processes = [];
let shuttingDown = false;

function prefixAndWrite(stream, label, data) {
  const text = data.toString();
  const lines = text.split(/\r?\n/);
  for (const line of lines) {
    if (!line) continue;
    stream.write(`[${label}] ${line}\n`);
  }
}

function startProcess({ label, cmd, args, cwd, shell = false }) {
  const child = spawn(cmd, args, {
    cwd,
    stdio: ['inherit', 'pipe', 'pipe'],
    shell,
    env: process.env,
  });

  child.stdout.on('data', (d) => prefixAndWrite(process.stdout, label, d));
  child.stderr.on('data', (d) => prefixAndWrite(process.stderr, label, d));

  child.on('exit', (code) => {
    if (shuttingDown) return;
    if (code !== 0) {
      console.error(`[${label}] exited with code ${code}. Shutting down all processes.`);
      shutdown(code || 1);
    }
  });

  processes.push(child);
  return child;
}

function shutdown(exitCode = 0) {
  if (shuttingDown) return;
  shuttingDown = true;

  for (const p of processes) {
    if (!p.killed) {
      try {
        p.kill('SIGTERM');
      } catch {
        // Ignore process kill failures during shutdown.
      }
    }
  }

  setTimeout(() => {
    for (const p of processes) {
      if (!p.killed) {
        try {
          p.kill('SIGKILL');
        } catch {
          // Ignore force-kill failures.
        }
      }
    }
    process.exit(exitCode);
  }, 500);
}

process.on('SIGINT', () => shutdown(0));
process.on('SIGTERM', () => shutdown(0));

startProcess({
  label: 'NEXT',
  cmd: fs.existsSync(nextCmd) ? nextCmd : 'next',
  args: ['dev', '--turbopack', '-p', '9002'],
  cwd: root,
  shell: false,
});

startProcess({
  label: 'BACKEND',
  cmd: pythonCmd,
  args: ['-m', 'uvicorn', 'main:app', '--reload', '--host', '127.0.0.1', '--port', '8001'],
  cwd: path.join(root, 'backend'),
  shell: false,
});
