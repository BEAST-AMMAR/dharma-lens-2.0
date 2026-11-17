import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import axios from 'axios';
import { createClient } from '@supabase/supabase-js';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from mounted .env file or Docker environment
const envPath = path.resolve(__dirname, '../.env');
if (fs.existsSync(envPath)) {
  dotenv.config({ path: envPath });
}
dotenv.config();

// ──────────────────────────────────────────────────────────────────
// FAIL-FAST STARTUP VALIDATION — No hardcoded fallback credentials
// ──────────────────────────────────────────────────────────────────
const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl) {
  console.error("[FATAL] VITE_SUPABASE_URL environment variable is missing. Refusing to start.");
  process.exit(1);
}
if (!supabaseKey) {
  console.error("[FATAL] VITE_SUPABASE_ANON_KEY environment variable is missing. Refusing to start.");
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

// ──────────────────────────────────────────────────────────────────
// SAFE PYTHON ENGINE BASE URL RESOLUTION
// ──────────────────────────────────────────────────────────────────
function getPythonEngineBaseUrl() {
  const raw = process.env.PYTHON_ENGINE_URL || 'http://localhost:8000/process';
  try {
    const parsed = new URL(raw);
    return `${parsed.protocol}//${parsed.host}`;
  } catch {
    return raw.replace(/\/process\/?$/, '').replace(/\/+$/, '');
  }
}

const pythonBaseUrl = getPythonEngineBaseUrl();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(helmet({ crossOriginResourcePolicy: false }));
app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'VidhiChakshu API Gateway', version: '3.0.0' });
});

// Proxy endpoint for processing documents
app.post('/api/process-document', async (req, res) => {
  const { documentPath, config } = req.body;
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error } = await supabase.auth.getUser(token);
    
    if (error || !user) {
      return res.status(401).json({ error: 'Invalid authentication token' });
    }

    const mlResponse = await axios.post(`${pythonBaseUrl}/process`, {
      documentPath,
      config
    }, {
      headers: {
        'Authorization': authHeader
      },
      timeout: 60000
    });

    res.json(mlResponse.data);

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Error in processing:', errorMessage);
    const statusCode = error.response?.status || 500;
    res.status(statusCode).json({ 
      success: false, 
      error: error.response?.data?.error || 'Internal Server Error forwarding to ML Engine' 
    });
  }
});

// Proxy endpoint for checking job status
app.get('/api/job/:jobId', async (req, res) => {
  const { jobId } = req.params;
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error } = await supabase.auth.getUser(token);
    if (error || !user) {
      return res.status(401).json({ error: 'Invalid authentication token' });
    }

    const mlResponse = await axios.get(`${pythonBaseUrl}/job/${jobId}`, {
      headers: {
        'Authorization': authHeader
      },
      timeout: 10000
    });
    res.json(mlResponse.data);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Error checking job:', errorMessage);
    const statusCode = error.response?.status || 500;
    res.status(statusCode).json({ status: 'failed', error: 'Could not fetch job status' });
  }
});

// Proxy endpoint for document chat
app.post('/api/chat', async (req, res) => {
  const { document_text, query, chat_history, config } = req.body;
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error } = await supabase.auth.getUser(token);
    if (error || !user) {
      return res.status(401).json({ error: 'Invalid authentication token' });
    }

    const mlResponse = await axios.post(`${pythonBaseUrl}/chat`, {
      document_text,
      query,
      chat_history,
      config
    }, {
      headers: {
        'Authorization': authHeader
      },
      timeout: 45000
    });

    res.json(mlResponse.data);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Error in chat:', errorMessage);
    const statusCode = error.response?.status || 500;
    res.status(statusCode).json({ success: false, error: 'Could not fetch chat response' });
  }
});

// Proxy endpoint for generating certified PDF report
app.post('/api/export-pdf', async (req, res) => {
  const { document_data } = req.body;
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error } = await supabase.auth.getUser(token);
    if (error || !user) {
      return res.status(401).json({ error: 'Invalid authentication token' });
    }

    const mlResponse = await axios.post(`${pythonBaseUrl}/export-pdf`, {
      document_data
    }, {
      headers: {
        'Authorization': authHeader
      },
      responseType: 'arraybuffer',
      timeout: 30000
    });

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'attachment; filename="VidhiChakshu_Certified_Legal_Brief.pdf"');
    res.send(mlResponse.data);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Error generating PDF:', errorMessage);
    res.status(500).json({ error: 'Failed to generate PDF report' });
  }
});

app.use((req, res) => {
  res.status(404).json({ error: 'Not Found' });
});

app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal Server Error' });
});

app.listen(PORT, () => {
  console.log(`VidhiChakshu API Gateway running on port ${PORT}`);
  console.log(`Python ML Engine base URL: ${pythonBaseUrl}`);
});
