require('dotenv').config();
const { downloadFile } = require('../storage-helper');

module.exports = async function handler(req, res) {
  try {
    const filename = req.query.filename || req.query.path || req.query["filename"];
    const source = filename || (req.url ? decodeURIComponent(req.url.split('/').pop()) : null);
    if (!source) {
      return res.status(400).json({ error: 'filename is required' });
    }
    const buffer = await downloadFile(source);
    res.setHeader('Content-Disposition', `attachment; filename="${source}"`);
    res.setHeader('Content-Type', 'application/octet-stream');
    res.status(200).send(buffer);
  } catch (err) {
    res.status(err.statusCode || 500).json({ error: err.message });
  }
};
