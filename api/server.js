const express = require('express');
require('dotenv').config();
const { listFiles, downloadFile, isSupabaseReady } = require('./storage-helper');

if (isSupabaseReady()) {
  console.log('API using Supabase storage');
} else {
  console.log('SUPABASE credentials not found; starting in local filesystem mode');
}

const app = express();
app.use(express.json());

app.get('/files', async (req, res) => {
  try {
    const data = await listFiles();
    return res.json(data);
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
});

app.get('/download/:filename', async (req, res) => {
  try {
    const filename = req.params.filename;
    const buffer = await downloadFile(filename);
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.send(buffer);
  } catch (err) {
    res.status(err.statusCode || 500).json({ error: err.message });
  }
});

function startServer(port) {
  const server = app.listen(port, () => console.log(`API server running on http://localhost:${port}`));
  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      const nextPort = Number(port) + 1;
      console.log(`Port ${port} is busy, trying ${nextPort}`);
      startServer(nextPort);
      return;
    }
    throw err;
  });
}

startServer(Number(process.env.PORT || 3000));
