const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

function getEnv() {
  return {
    supabaseUrl: process.env.SUPABASE_URL,
    supabaseKey: process.env.SUPABASE_KEY,
    bucketName: process.env.BUCKET_NAME,
    localFolder: process.env.LOCAL_STORAGE_FOLDER || '../samples',
  };
}

function isSupabaseReady() {
  const env = getEnv();
  return Boolean(env.supabaseUrl && env.supabaseKey && env.bucketName);
}

function getStorage() {
  const env = getEnv();
  if (!isSupabaseReady()) {
    return null;
  }
  const client = createClient(env.supabaseUrl, env.supabaseKey);
  return client.storage;
}

function getLocalFolderPath() {
  const env = getEnv();
  return path.resolve(__dirname, '..', env.localFolder);
}

function listLocalFiles() {
  const folder = getLocalFolderPath();
  if (!fs.existsSync(folder)) return [];
  return fs
    .readdirSync(folder)
    .filter((name) => fs.statSync(path.join(folder, name)).isFile())
    .map((name) => ({ name }));
}

async function listFiles() {
  const storage = getStorage();
  if (!storage) return listLocalFiles();
  const { bucketName } = getEnv();
  const { data, error } = await storage.from(bucketName).list();
  if (error) throw new Error(error.message);
  return data;
}

async function downloadFile(filename) {
  const storage = getStorage();
  if (!storage) {
    const filePath = path.resolve(getLocalFolderPath(), filename);
    if (!fs.existsSync(filePath)) {
      const error = new Error('Not found');
      error.statusCode = 404;
      throw error;
    }
    return fs.readFileSync(filePath);
  }

  const { bucketName } = getEnv();
  const { data, error } = await storage.from(bucketName).download(filename);
  if (error) throw new Error(error.message);
  return Buffer.from(await data.arrayBuffer());
}

module.exports = {
  getEnv,
  isSupabaseReady,
  listFiles,
  downloadFile,
  getLocalFolderPath,
};
