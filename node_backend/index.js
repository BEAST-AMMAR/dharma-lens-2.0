import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';
import { createClient } from '@supabase/supabase-js';

import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../.env.local') });
dotenv.config({ path: path.resolve(__dirname, '../.env') });
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
// SAFE PYTHON ENGINE BASE URL RESOLUTION — No brittle string replace
// ──────────────────────────────────────────────────────────────────
function getPythonEngineBaseUrl() {
  const raw = process.env.PYTHON_ENGINE_URL || 'http://localhost:8000/process';
  try {
    const parsed = new URL(raw);
    return `${parsed.protocol}//${parsed.host}`;
  } catch {
    // If URL parsing fails, strip trailing path segments manually
    return raw.replace(/\/process\/?$/, '').replace(/\/+$/, '');
  }
}

const pythonBaseUrl = getPythonEngineBaseUrl();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'Dharma Lens API Gateway' });
});

// Proxy endpoint for processing documents
app.post('/api/process-document', async (req, res) => {
  const { documentPath, config } = req.body;
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    // 1. Verify User JWT via Supabase
    const { data: { user }, error } = await supabase.auth.getUser(authHeader.replace('Bearer ', ''));
    
    if (error || !user) {
      return res.status(401).json({ error: 'Invalid authentication token' });
    }

    // 2. Forward the request to Python ML Engine
    const mlResponse = await axios.post(`${pythonBaseUrl}/process`, {
      documentPath,
      config
    }, {
      headers: {
        'Authorization': authHeader
      }
    });

    // 3. Return the ML response (job_id) back to the frontend
    res.json(mlResponse.data);

  } catch (error) {
    console.error('Error in processing:', error.message);
    res.status(500).json({ 
      success: false, 
      error: error.response?.data?.error || 'Internal Server Error forwarding to ML Engine' 
    });
  }
});

// Proxy endpoint for checking job status (Secure: enforces JWT check)
app.get('/api/job/:jobId', async (req, res) => {
  const { jobId } = req.params;
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const { data: { user }, error } = await supabase.auth.getUser(authHeader.replace('Bearer ', ''));
    if (error || !user) {
      return res.status(401).json({ error: 'Invalid authentication token' });
    }

    const mlResponse = await axios.get(`${pythonBaseUrl}/job/${jobId}`, {
      headers: {
        'Authorization': authHeader
      }
    });
    res.json(mlResponse.data);
  } catch (error) {
    console.error('Error checking job:', error.message);
    res.status(500).json({ status: 'failed', error: 'Could not fetch job status' });
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
    const { data: { user }, error } = await supabase.auth.getUser(authHeader.replace('Bearer ', ''));
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
      }
    });

    res.json(mlResponse.data);
  } catch (error) {
    console.error('Error in chat:', error.message);
    res.status(500).json({ success: false, error: 'Could not fetch chat response' });
  }
});

app.listen(PORT, () => {
  console.log(`Dharma Lens API Gateway running on port ${PORT}`);
  console.log(`Python ML Engine base URL: ${pythonBaseUrl}`);
});
