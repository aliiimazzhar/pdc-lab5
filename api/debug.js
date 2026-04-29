require('dotenv').config();
const { getEnv, isSupabaseReady, getStorage } = require('./storage-helper');

module.exports = async function handler(req, res) {
  try {
    const env = getEnv();
    const ready = isSupabaseReady();
    const masked = {
      SUPABASE_URL: env.supabaseUrl ? true : false,
      SUPABASE_KEY: env.supabaseKey ? true : false,
      BUCKET_NAME: env.bucketName || null,
      LOCAL_FOLDER: env.localFolder || null,
    };

    const result = { env: masked, isSupabaseReady: ready };

    if (ready) {
      const storage = getStorage();
      try {
        const { data, error } = await storage.from(env.bucketName).list();
        if (error) result.listError = error.message || error;
        else result.listCount = Array.isArray(data) ? data.length : null;
      } catch (err) {
        result.listError = err.message || String(err);
      }
    }

    res.status(200).json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
