const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3000;

const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

app.use(express.json());

app.get('/test-get', (req, res) => {
  try {
    const base64Image = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
    
    res.json({
      imageBase64: base64Image
    });
  } catch (error) {
    console.error('Error in /test-get:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/test-post-form-data', upload.single('image'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    const imageBuffer = req.file.buffer;
    const base64Image = imageBuffer.toString('base64');
    const mimeType = req.file.mimetype;

    console.log(`Received image: ${req.file.originalname}, Size: ${req.file.size} bytes, Type: ${mimeType}`);

    res.json({
      message: 'Image uploaded successfully',
      filename: req.file.originalname,
      size: req.file.size,
      mimeType: mimeType,
      imageBase64: base64Image
    });
  } catch (error) {
    console.error('Error in /test-post-form-data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

app.listen(port, () => {
  console.log(`API Server running on http://localhost:${port}`);
  console.log('\nAvailable endpoints:');
  console.log('GET  /test-get - Returns image as base64');
  console.log('POST /test-post-form-data - Upload image via form data');
  console.log('GET  /health - Health check');
});

module.exports = app;