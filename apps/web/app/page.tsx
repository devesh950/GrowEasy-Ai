'use client';

import { useMemo, useRef, useState } from 'react';
import Papa from 'papaparse';

type PreviewRow = Record<string, string>;

type CrmRecord = {
  created_at: string;
  name: string;
  email: string;
  country_code: string;
  mobile_without_country_code: string;
  company: string;
  city: string;
  state: string;
  country: string;
  lead_owner: string;
  crm_status: string;
  crm_note: string;
  data_source: string;
  possession_time: string;
  description: string;
};

type ImportResponse = {
  records: CrmRecord[];
  skipped: Array<{ rowNumber: number; reason: string; originalRow: PreviewRow }>;
  totalImported: number;
  totalSkipped: number;
  batchesProcessed: number;
};

type CsvParseResult = {
  data: PreviewRow[];
  meta: {
    fields?: string[];
  };
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:4000';

const crmColumns: Array<keyof CrmRecord> = [
  'created_at',
  'name',
  'email',
  'country_code',
  'mobile_without_country_code',
  'company',
  'city',
  'state',
  'country',
  'lead_owner',
  'crm_status',
  'crm_note',
  'data_source',
  'possession_time',
  'description'
];

export default function HomePage() {
  const [fileName, setFileName] = useState('');
  const [headers, setHeaders] = useState<string[]>([]);
  const [previewRows, setPreviewRows] = useState<PreviewRow[]>([]);
  const [result, setResult] = useState<ImportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const resultsScrollRef = useRef<HTMLDivElement | null>(null);

  const previewCount = useMemo(() => previewRows.length, [previewRows]);

  function handleFile(file: File | null) {
    setError('');
    setResult(null);
    if (!file) return;

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result ?? '');
      const parsed = Papa.parse(text, {
        header: true,
        skipEmptyLines: true,
        dynamicTyping: false
      }) as CsvParseResult;

      const rows = parsed.data.slice(0, 8).map((row) =>
        Object.fromEntries(Object.entries(row).map(([key, value]) => [key, String(value ?? '')]))
      );

      setHeaders(parsed.meta.fields ?? Object.keys(rows[0] ?? {}));
      setPreviewRows(rows);
    };
    reader.readAsText(file);
  }

  function openFilePicker() {
    fileInputRef.current?.click();
  }

  function handleDrop(event: React.DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setDragActive(false);
    handleFile(event.dataTransfer.files?.[0] ?? null);
  }

  function scrollResults(delta: number) {
    resultsScrollRef.current?.scrollBy({ left: delta, behavior: 'smooth' });
  }

  async function confirmImport() {
    if (!fileName) return;

    setLoading(true);
    setError('');
    try {
      const file = fileInputRef.current?.files?.[0];
      if (!file) {
        throw new Error('Select a CSV file first.');
      }

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${apiBaseUrl}/api/import-csv`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Import failed with status ${response.status}`);
      }

      const payload = (await response.json()) as ImportResponse;
      setResult(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">GrowEasy CRM</p>
          <h1>Import messy CSVs with AI-grade field mapping.</h1>
          <p className="lede">
            Drop in exports from ads, sheets, CRMs, or hand-built spreadsheets. Preview rows instantly, confirm the import, and get structured CRM records back in a clean, modern workflow.
          </p>

          <div className="hero-actions">
            <button className="primary-button" onClick={openFilePicker} type="button">
              Choose CSV file
            </button>
            <a className="ghost-button" href="#results">
              View import results
            </a>
          </div>

          <div className="workflow-pills" aria-label="Import workflow">
            <span>Upload</span>
            <span>Preview</span>
            <span>Confirm</span>
            <span>Parse</span>
          </div>
        </div>

        <aside className="hero-aside">
          <div className="glass-card accent-card">
            <span className="card-label">Ready for anything</span>
            <strong>Facebook lead exports, Google sheets, CRM dumps, sales reports</strong>
            <p>Rows are previewed locally first, then the backend extracts GrowEasy CRM fields in batches.</p>
          </div>
          <div className="mini-grid">
            <div className="mini-card">
              <span>Local preview</span>
              <strong>No AI yet</strong>
            </div>
            <div className="mini-card">
              <span>Backend import</span>
              <strong>On confirm only</strong>
            </div>
          </div>
        </aside>
      </section>

      <section className="panel upload-panel">
        <div className="section-heading section-heading-tight">
          <div>
            <h2>Step 1. Upload CSV</h2>
            <p>Use drag and drop or the file picker. Preview is local only.</p>
          </div>
          <span className="status-chip status-chip-muted">{fileName ? 'File selected' : 'Waiting for file'}</span>
        </div>

        <label
          className={`dropzone ${dragActive ? 'dropzone-active' : ''}`}
          htmlFor="csv-input"
          onDragEnter={() => setDragActive(true)}
          onDragOver={(event) => {
            event.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            id="csv-input"
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => handleFile(event.target.files?.[0] ?? null)}
          />
          <div className="dropzone-icon">⇪</div>
          <strong>Drag & drop your CSV here</strong>
          <span>{fileName || 'Or click to browse. Preview appears immediately after selection.'}</span>
        </label>

        <div className="upload-footer">
          <div className="file-meta">
            <span className="file-name">{fileName || 'No file selected yet'}</span>
            <span className="hint">The backend runs only after you confirm.</span>
          </div>
          <button className="primary-button" onClick={confirmImport} disabled={!fileName || loading} type="button">
            {loading ? 'Processing...' : 'Confirm import'}
          </button>
        </div>
        {error ? <p className="error">{error}</p> : null}
      </section>

      {previewRows.length > 0 ? (
        <section className="panel">
          <div className="section-heading">
            <div>
              <h2>Step 2. Preview</h2>
              <p>{previewCount} rows shown locally before AI processing</p>
            </div>
            <span className="status-chip">Preview ready</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>{headers.map((header) => <th key={header}>{header}</th>)}</tr>
              </thead>
              <tbody>
                {previewRows.map((row, index) => (
                  <tr key={index}>
                    {headers.map((header) => <td key={header}>{row[header] ?? ''}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {result ? (
        <section className="panel result-panel" id="results">
          <div className="section-heading">
            <div>
              <h2>Step 3. Parsed result</h2>
              <p>Structured output returned from the backend</p>
            </div>
            <span className="status-chip status-chip-success">Import complete</span>
          </div>

          <div className="stats">
            <article>
              <span>Total imported</span>
              <strong>{result.totalImported}</strong>
            </article>
            <article>
              <span>Total skipped</span>
              <strong>{result.totalSkipped}</strong>
            </article>
            <article>
              <span>Batches processed</span>
              <strong>{result.batchesProcessed}</strong>
            </article>
          </div>

          <div className="table-controls">
            <p className="table-hint">Scroll inside the table to view all columns and full field values.</p>
            <div className="table-actions">
              <button type="button" className="ghost-button small" onClick={() => scrollResults(-420)}>◀ Left</button>
              <button type="button" className="ghost-button small" onClick={() => scrollResults(420)}>Right ▶</button>
            </div>
          </div>
          <div className="table-wrap large results-scroll" ref={resultsScrollRef}>
            <table>
              <thead>
                <tr>{crmColumns.map((column) => <th key={column}>{column}</th>)}</tr>
              </thead>
              <tbody>
                {result.records.map((record, index) => (
                  <tr key={index}>
                    {crmColumns.map((column) => {
                      const value = record[column] ?? '';
                      const isLongText = column === 'crm_note' || column === 'description';
                      return (
                        <td key={column} className={isLongText ? 'long-cell' : ''} title={String(value)}>
                          {column === 'crm_status' && value ? <span className={`value-pill value-pill-${String(value).toLowerCase()}`}>{value}</span> : value}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {result.skipped.length > 0 ? (
            <>
              <div className="section-heading skipped-heading">
                <div>
                  <h2>Skipped rows</h2>
                  <p>Rows missing both email and mobile number</p>
                </div>
                <span className="status-chip status-chip-warning">{result.totalSkipped} skipped</span>
              </div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Row</th>
                      <th>Reason</th>
                      <th>Original Data</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.skipped.map((row) => (
                      <tr key={row.rowNumber}>
                        <td><span className="row-badge">{row.rowNumber}</span></td>
                        <td>{row.reason}</td>
                        <td className="mono-cell">{JSON.stringify(row.originalRow)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : null}
        </section>
      ) : null}
    </main>
  );
}
