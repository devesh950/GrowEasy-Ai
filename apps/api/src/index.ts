import cors from 'cors';
import dotenv from 'dotenv';
import express from 'express';
import multer from 'multer';
import { parse } from 'csv-parse/sync';
import { extractCrmRecords } from './ai.js';
import type { ImportResponse, SkippedRecord } from './types.js';

dotenv.config();

const app = express();
const upload = multer({ storage: multer.memoryStorage() });
const port = Number(process.env.API_PORT ?? 4000);
const allowedOrigins = new Set(
  (process.env.FRONTEND_ORIGINS ?? process.env.FRONTEND_ORIGIN ?? 'http://localhost:3000,http://localhost:3001')
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean)
);

app.use(
  cors({
    origin(origin, callback) {
      if (!origin || allowedOrigins.has(origin) || /^http:\/\/localhost:\d+$/.test(origin)) {
        callback(null, true);
        return;
      }

      callback(new Error(`CORS blocked for origin: ${origin}`));
    }
  })
);
app.use(express.json({ limit: '10mb' }));

app.get('/health', (_request, response) => {
  response.json({ ok: true });
});

app.post('/api/import-csv', upload.single('file'), async (request, response) => {
  try {
    if (!request.file) {
      return response.status(400).json({ message: 'CSV file is required.' });
    }

    const csvText = request.file.buffer.toString('utf8');
    const parsedRows = parse(csvText, {
      columns: true,
      skip_empty_lines: true,
      relax_column_count: true,
      trim: true
    }) as Record<string, string>[];

    const normalizedRows = parsedRows.map((row) =>
      Object.fromEntries(
        Object.entries(row).map(([key, value]) => [String(key).trim(), String(value ?? '').trim()])
      )
    );

    const skipped: SkippedRecord[] = [];
    const rowsForExtraction: Record<string, string>[] = [];

    normalizedRows.forEach((row, index) => {
      const rowText = Object.values(row).join(' ');
      const hasEmail = /@/.test(rowText);
      const hasPhone = /\d{7,}/.test(rowText);

      if (!hasEmail && !hasPhone) {
        skipped.push({ rowNumber: index + 2, reason: 'Missing both email and mobile number', originalRow: row });
        return;
      }

      rowsForExtraction.push(row);
    });

    const { records, batchesProcessed } = await extractCrmRecords(rowsForExtraction, 20);

    const payload: ImportResponse = {
      records,
      skipped,
      totalImported: records.length,
      totalSkipped: skipped.length,
      batchesProcessed
    };

    return response.json(payload);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to import CSV';
    return response.status(500).json({ message });
  }
});

app.listen(port, () => {
  console.log(`GrowEasy API listening on http://localhost:${port}`);
});
