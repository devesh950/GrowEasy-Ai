# GrowEasy CSV Importer

AI-powered CSV importer for GrowEasy CRM. The frontend lets users upload a CSV, preview it locally, and confirm the import. The backend parses the uploaded file, extracts CRM fields in batches, and returns structured JSON records.

## Stack

- Frontend: Next.js 14, React 18, TypeScript
- Backend: Node.js, Express, TypeScript
- CSV parsing: `papaparse` in the browser, `csv-parse` on the server
- AI extraction: OpenAI API when `OPENAI_API_KEY` is available, with a deterministic fallback mapper otherwise

## Project Structure

- `apps/web` - Next.js UI for upload, preview, and import results
- `apps/api` - Express API for CSV parsing and AI extraction

## Setup

1. Install dependencies:

```bash
npm install
```

2. Configure environment variables:

```bash
copy .env.example .env
```

`FRONTEND_ORIGIN` is used by the API for CORS, and `NEXT_PUBLIC_API_BASE_URL` is used by the web app to call the API.

3. Run both apps:

```bash
npm run dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:4000

## API

`POST /api/import-csv`

Form data field:

- `file` - CSV file

Response includes:

- `records` - successfully parsed CRM records
- `skipped` - skipped rows with reasons
- `totalImported`
- `totalSkipped`
- `batchesProcessed`

## Notes

- The backend only skips a row when both email and mobile are missing.
- CRM statuses are normalized to the allowed GrowEasy values.
- Data source is kept blank unless it confidently matches the allowed list.
