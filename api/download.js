require('dotenv').config();
const { downloadFile } = require('./storage-helper');

module.exports = async function handler(req, res) {
  try {
    const filename = req.query.filename;
    if (!filename) {
      return res.status(400).json({ error: 'filename is required' });
    }
    const buffer = await downloadFile(filename);
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.setHeader('Content-Type', 'application/octet-stream');
    res.status(200).send(buffer);
  } catch (err) {
    res.status(err.statusCode || 500).json({ error: err.message });
  }
};
