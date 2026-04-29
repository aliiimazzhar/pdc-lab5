require('dotenv').config();
const { listFiles } = require('./storage-helper');

module.exports = async function handler(req, res) {
  try {
    const files = await listFiles();
    res.status(200).json(files);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
