// One-click start for InstaLearn (run by start-app.bat).
//   1. checks Node and installs/updates packages when package.json changed
//   2. makes sure .env.local has the Supabase settings (asks once)
//   3. sets up / updates the database (runs supabase/*.sql when they changed)
//   4. starts Expo and shows the QR code
// Flags: --tunnel (phone on another network), --force-db (re-run all SQL), --db-only (no Expo).

import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync, appendFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline/promises';
import { stdin, stdout } from 'node:process';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const ENV = join(ROOT, '.env.local');
const STATE = join(ROOT, '.setup-state.json');
const SQL_FILES = ['schema.sql', 'chat.sql', 'people.sql']; // order matters
const args = new Set(process.argv.slice(2));

const say = (s = '') => console.log(s);
const step = (n, s) => say(`\n[${n}/4] ${s}`);
const hash = (s) => createHash('sha256').update(s).digest('hex');
const readState = () => { try { return JSON.parse(readFileSync(STATE, 'utf8')); } catch { return {}; } };
const writeState = (s) => writeFileSync(STATE, JSON.stringify(s, null, 2));

function run(cmd, cmdArgs) {
  // One command string (no separate args) – avoids Node's shell-args warning on Windows.
  const r = spawnSync([cmd, ...cmdArgs].join(' '), { cwd: ROOT, stdio: 'inherit', shell: true });
  return r.status === 0;
}

function readEnv() {
  const env = {};
  if (!existsSync(ENV)) return env;
  for (const line of readFileSync(ENV, 'utf8').split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (m) env[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }
  return env;
}

function addEnv(key, value) {
  const prefix = existsSync(ENV) && !readFileSync(ENV, 'utf8').endsWith('\n') ? '\n' : '';
  appendFileSync(ENV, `${prefix}${key}=${value}\n`);
}

let rl = null; // one prompt reader for the whole run (re-creating it can drop pasted text on Windows)
async function ask(question) {
  rl ??= createInterface({ input: stdin, output: stdout, terminal: true });
  return (await rl.question(question)).trim().replace(/^["'\s]+|["'\s]+$/g, '');
}
function closeAsk() { rl?.close(); rl = null; }

// ---------------------------------------------------------------- 1. packages
async function packages(state) {
  step(1, 'Checking packages');
  const pkgHash = hash(readFileSync(join(ROOT, 'package.json'), 'utf8'));
  if (existsSync(join(ROOT, 'node_modules')) && state.packages === pkgHash) {
    say('    Up to date.');
    return false;
  }
  say('    Installing packages (first time can take a few minutes)...');
  if (!run('npm', ['install', '--no-audit', '--no-fund'])) {
    say('    Retrying with relaxed version checks...');
    if (!run('npm', ['install', '--no-audit', '--no-fund', '--legacy-peer-deps']))
      throw new Error('npm install failed – check the internet connection, or run upgrade-expo.bat.');
  }
  state.packages = pkgHash;
  writeState(state);
  return true; // packages changed -> start Expo with a clean cache
}

// ---------------------------------------------------------------- 2. .env.local
const URI_RE = /postgres(?:ql)?:\/\/\S+/;
const REGIONS = ['eu-central-1', 'eu-central-2', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-north-1', 'us-east-1', 'us-east-2',
  'us-west-1', 'us-west-2', 'ca-central-1', 'sa-east-1', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2'];

async function tryConnect(pg, uri) {
  // Supabase uses its own certificate; sslmode in the URL would force strict checking.
  const c = new pg.Client({ connectionString: uri.replace(/[?&]sslmode=[^&]*/g, ''), ssl: { rejectUnauthorized: false }, connectionTimeoutMillis: 10000 });
  await c.connect();
  return c;
}
const isWrongPassword = (e) => /password authentication failed/i.test(String(e?.message || e));

// Find the project's "Session pooler" address from just the password (tries each Supabase region).
async function findPooler(pg, ref, password) {
  const pw = encodeURIComponent(password);
  for (const region of REGIONS) {
    for (const host of ['aws-0', 'aws-1']) {
      const uri = `postgresql://postgres.${ref}:${pw}@${host}-${region}.pooler.supabase.com:5432/postgres`;
      try {
        const c = await tryConnect(pg, uri);
        await c.end();
        return { uri };
      } catch (e) {
        if (isWrongPassword(e)) return { wrongPassword: true };
        // "Tenant or user not found" / unknown host / timeout -> not this region, keep looking
      }
    }
  }
  return {};
}

function removeEnv(key) {
  if (!existsSync(ENV)) return;
  const lines = readFileSync(ENV, 'utf8').split(/\r?\n/).filter((l) => !l.startsWith(key + '='));
  writeFileSync(ENV, lines.join('\n'));
}

async function envFile() {
  step(2, 'Checking Supabase settings (.env.local)');
  let env = readEnv();

  if (!env.EXPO_PUBLIC_SUPABASE_URL) {
    let url = '';
    while (!/^https:\/\/[a-z0-9]+\.supabase\.co/.test(url))
      url = await ask('    Supabase Project URL (https://xxxx.supabase.co): ');
    addEnv('EXPO_PUBLIC_SUPABASE_URL', url.replace(/\/+$/, ''));
  }
  if (!env.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY) {
    say('    Supabase → Project Settings → API Keys → copy the "Publishable key" (starts with sb_publishable_).');
    let key = '';
    while (!key.startsWith('sb_publishable_')) key = await ask('    Paste the publishable key: ');
    addEnv('EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY', key);
  }
  env = readEnv();

  if (!env.SUPABASE_DB_URL) {
    const { default: pg } = await import('pg');
    const ref = (env.EXPO_PUBLIC_SUPABASE_URL.match(/https:\/\/([a-z0-9]+)\.supabase\.co/) || [])[1];
    say('\n    The DATABASE password is needed once, to create/update the tables.');
    say('    (Supabase → Project Settings → Database. Not your Supabase login password.)');
    say('    To paste in this window: right-click (or Ctrl+V), then press Enter.');
    for (;;) {
      const typed = await ask('    Database password: ');
      if (!typed) { say('    Nothing was typed.'); continue; }
      let uri = '';
      const m = typed.match(URI_RE);
      if (m) {
        // Also accepted: the full "Session pooler" URI.
        uri = m[0];
        if (uri.includes('[YOUR-PASSWORD]')) uri = uri.replace('[YOUR-PASSWORD]', encodeURIComponent(await ask('    Database password: ')));
        try {
          await (await tryConnect(pg, uri)).end();
        } catch (e) {
          say(isWrongPassword(e) ? '    Wrong password – try again.' : '    Could not connect with that URI: ' + (e.message || e));
          continue;
        }
      } else {
        say('    Connecting to your database (can take up to a minute)...');
        const r = await findPooler(pg, ref, typed);
        if (r.wrongPassword) { say('    Wrong password – try again (or reset it in Supabase → Project Settings → Database).'); continue; }
        if (!r.uri) {
          say('    Could not find the database server automatically.');
          say('    Instead, paste the URI: Supabase → "Connect" (top bar) → "Session pooler" → copy.');
          continue;
        }
        uri = r.uri;
      }
      addEnv('SUPABASE_DB_URL', uri);
      say('    Connected. Saved in .env.local (stays on your computer, not part of the app).');
      break;
    }
  }
  closeAsk();
  say('    OK.');
  return readEnv();
}

// ---------------------------------------------------------------- 3. database
async function database(env, state) {
  step(3, 'Setting up the database');
  const files = SQL_FILES.map((f) => ({ name: f, sql: readFileSync(join(ROOT, 'supabase', f), 'utf8') }));
  const sqlHash = hash(files.map((f) => f.sql).join('\n'));
  if (state.database === sqlHash && !args.has('--force-db')) {
    say('    Up to date.');
    return;
  }

  const { default: pg } = await import('pg');
  let client;
  try {
    client = await tryConnect(pg, env.SUPABASE_DB_URL);
  } catch (e) {
    const msg = String(e.message || e);
    if (isWrongPassword(e) || /Tenant or user not found|ENOTFOUND|ENETUNREACH|EHOSTUNREACH/i.test(msg)) {
      removeEnv('SUPABASE_DB_URL'); // ask again next time
      throw new Error('The saved database password/address no longer works (password changed?). Run this file again and type the new password.');
    }
    throw new Error('Database connection failed (check the internet connection): ' + msg);
  }
  try {
    for (const f of files) {
      process.stdout.write(`    Running ${f.name} ... `);
      await client.query(f.sql);
      say('done');
    }
    const { rows } = await client.query(
      'select count(*)::int as users, count(p.id)::int as profiles from auth.users u left join public.profiles p on p.id = u.id',
    );
    say(`    Users: ${rows[0].users}, with profiles: ${rows[0].profiles}.`);
  } finally {
    await client.end();
  }
  state.database = sqlHash;
  writeState(state);
}

// ---------------------------------------------------------------- 4. Expo
function expo(clean) {
  step(4, 'Starting the app');
  say('    Wait for the QR code, then scan it: iPhone → Camera app, Android → Expo Go → "Scan QR code".');
  say('    Tip: do not click inside this window. If the title shows "Select", press Esc.');
  say('    To stop: press Ctrl+C.\n');
  const expoArgs = ['expo', 'start'];
  if (clean) expoArgs.push('--clear');
  if (args.has('--tunnel')) expoArgs.push('--tunnel');
  run('npx', expoArgs);
}

// ---------------------------------------------------------------- main
try {
  const [major] = process.versions.node.split('.').map(Number);
  if (major < 20) throw new Error(`Node.js ${process.versions.node} is too old. Install the LTS version from https://nodejs.org`);
  say('InstaLearn – one-click start');
  const state = readState();
  const changed = await packages(state);
  const env = await envFile();
  await database(env, state);
  if (!args.has('--db-only')) expo(changed);
  else say('\nDatabase is ready.');
} catch (e) {
  say('\n  ✖ ' + (e.message || e));
  process.exitCode = 1;
}
