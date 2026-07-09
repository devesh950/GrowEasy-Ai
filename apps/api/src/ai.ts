import OpenAI from 'openai';
import type { CrmRecord, CrmStatus, DataSource } from './types.js';

const allowedStatuses: CrmStatus[] = ['GOOD_LEAD_FOLLOW_UP', 'DID_NOT_CONNECT', 'BAD_LEAD', 'SALE_DONE'];
const allowedSources: DataSource[] = ['leads_on_demand', 'meridian_tower', 'eden_park', 'varah_swamy', 'sarjapur_plots'];

const statusHints: Array<[RegExp, CrmStatus]> = [
  [/sale|closed|won|deal/i, 'SALE_DONE'],
  [/follow|interested|warm|good/i, 'GOOD_LEAD_FOLLOW_UP'],
  [/not connect|busy|call back|callback|no answer|unreachable/i, 'DID_NOT_CONNECT'],
  [/not interested|spam|invalid|bad lead|wrong number/i, 'BAD_LEAD']
];

const sourceHints: Array<[RegExp, DataSource]> = [
  [/leads? on demand/i, 'leads_on_demand'],
  [/meridian tower/i, 'meridian_tower'],
  [/eden park/i, 'eden_park'],
  [/varah swamy/i, 'varah_swamy'],
  [/sarjapur plots/i, 'sarjapur_plots']
];

function normalizeWhitespace(value: string): string {
  return value.replace(/\s+/g, ' ').trim();
}

function firstMatch(values: string[], regex: RegExp): string {
  return values.find((value) => regex.test(value)) ?? '';
}

function extractEmails(text: string): string[] {
  return text.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi) ?? [];
}

function extractPhones(text: string): string[] {
  return text.match(/(?:\+?\d[\d\s().-]{7,}\d)/g)?.map((value) => value.replace(/[^\d+]/g, '')) ?? [];
}

function splitPhone(phone: string): { countryCode: string; mobile: string } {
  if (!phone.startsWith('+')) {
    return { countryCode: '', mobile: phone.replace(/\D/g, '') };
  }

  const digits = phone.replace(/\D/g, '');
  const countryCode = digits.slice(0, Math.min(3, Math.max(1, digits.length - 10)));
  return {
    countryCode: countryCode ? `+${countryCode}` : '',
    mobile: digits.slice(countryCode.length)
  };
}

function mapStatus(text: string): CrmStatus | '' {
  for (const [pattern, status] of statusHints) {
    if (pattern.test(text)) return status;
  }
  return '';
}

function mapDataSource(text: string): DataSource {
  for (const [pattern, source] of sourceHints) {
    if (pattern.test(text)) return source;
  }
  return '';
}

function joinNotes(parts: string[]): string {
  return parts.filter(Boolean).map(normalizeWhitespace).join(' | ');
}

function isAllowedStatus(value: string): value is CrmStatus {
  return allowedStatuses.includes(value as CrmStatus);
}

function isAllowedSource(value: string): value is DataSource {
  return allowedSources.includes(value as DataSource);
}

function looksLikeLeadOwner(value: string): boolean {
  const normalized = normalizeWhitespace(value);
  if (!normalized) return false;
  if (/@/.test(normalized)) return false;
  if (/\d/.test(normalized)) return false;
  if (/^(test|unknown|n\/a|na|none)$/i.test(normalized)) return false;
  if (/(inc|llc|ltd|corp|company|solutions|tech|group|gmail|email|phone|mobile)/i.test(normalized)) return false;
  return /^[A-Za-z][A-Za-z .'-]{1,60}$/.test(normalized);
}

function normalizeExtractedRecord(record: Partial<CrmRecord>): CrmRecord {
  const email = normalizeWhitespace(String(record.email ?? ''));
  const mobile = normalizeWhitespace(String(record.mobile_without_country_code ?? '')).replace(/\D/g, '');
  const countryCode = normalizeWhitespace(String(record.country_code ?? ''));
  const leadOwner = normalizeWhitespace(String(record.lead_owner ?? ''));
  const crmStatus = normalizeWhitespace(String(record.crm_status ?? ''));
  const dataSource = normalizeWhitespace(String(record.data_source ?? ''));
  const createdAt = normalizeWhitespace(String(record.created_at ?? ''));

  return {
    created_at: createdAt && !Number.isNaN(Date.parse(createdAt)) ? new Date(createdAt).toISOString() : new Date().toISOString(),
    name: normalizeWhitespace(String(record.name ?? '')),
    email,
    country_code: countryCode.startsWith('+') ? countryCode : countryCode ? `+${countryCode.replace(/\D/g, '')}` : '',
    mobile_without_country_code: mobile,
    company: normalizeWhitespace(String(record.company ?? '')),
    city: normalizeWhitespace(String(record.city ?? '')),
    state: normalizeWhitespace(String(record.state ?? '')),
    country: normalizeWhitespace(String(record.country ?? '')),
    lead_owner: looksLikeLeadOwner(leadOwner) ? leadOwner : '',
    crm_status: isAllowedStatus(crmStatus) ? crmStatus : '',
    crm_note: normalizeWhitespace(String(record.crm_note ?? '')),
    data_source: isAllowedSource(dataSource as DataSource) ? (dataSource as DataSource) : '',
    possession_time: normalizeWhitespace(String(record.possession_time ?? '')),
    description: normalizeWhitespace(String(record.description ?? ''))
  };
}

function buildRecord(row: Record<string, string>): CrmRecord | null {
  const values = Object.values(row).map((value) => String(value ?? '').trim());
  const combined = values.join(' | ');
  const emails = extractEmails(combined);
  const phones = extractPhones(combined);

  if (emails.length === 0 && phones.length === 0) return null;

  const primaryEmail = emails[0] ?? '';
  const primaryPhone = phones[0] ?? '';
  const extraEmails = emails.slice(1);
  const extraPhones = phones.slice(1);

  const name = firstMatch(values, /[A-Za-z]+\s+[A-Za-z]+/);
  const createdAt = firstMatch(values, /\d{4}-\d{2}-\d{2}(?:[T\s]\d{2}:\d{2}(?::\d{2})?)?/);
  const company = firstMatch(values, /(?:inc|llc|ltd|corp|company|solutions|tech|group)/i);
  const city = firstMatch(values, /(?:mumbai|delhi|bangalore|bengaluru|pune|hyderabad|chennai|kolkata|ahmedabad)/i);
  const state = firstMatch(values, /(?:maharashtra|karnataka|delhi|telangana|tamil nadu|gujarat|rajasthan|kerala)/i);
  const country = firstMatch(values, /(?:india|usa|united states|uk|united kingdom|uae)/i);
  const leadOwner = firstMatch(
    Object.entries(row)
      .filter(([key]) => /owner|assigned|agent|sales rep|representative/i.test(key))
      .map(([, value]) => value),
    /^[A-Za-z][A-Za-z .'-]{1,60}$/
  );
  const status = mapStatus(combined);
  const dataSource = mapDataSource(combined);
  const description = normalizeWhitespace(values.join(' ')).slice(0, 500);

  const notes = joinNotes([
    values.filter((value) => /remark|note|comment|follow|busy|interested|not interested|resched|callback/i.test(value)).join(' '),
    extraEmails.length ? `Additional emails: ${extraEmails.join(', ')}` : '',
    extraPhones.length ? `Additional phones: ${extraPhones.join(', ')}` : ''
  ]);

  const phoneParts = splitPhone(primaryPhone);

  const crmRecord: CrmRecord = normalizeExtractedRecord({
    created_at: createdAt && !Number.isNaN(Date.parse(createdAt)) ? new Date(createdAt).toISOString() : new Date().toISOString(),
    name,
    email: primaryEmail,
    country_code: phoneParts.countryCode,
    mobile_without_country_code: phoneParts.mobile,
    company,
    city,
    state,
    country,
    lead_owner: leadOwner,
    crm_status: status,
    crm_note: notes,
    data_source: dataSource,
    possession_time: '',
    description
  });

  return crmRecord;
}

function fallbackExtract(rows: Record<string, string>[]): CrmRecord[] {
  return rows.map((row) => buildRecord(row)).filter((record): record is CrmRecord => Boolean(record));
}

function parseJsonArray(content: string): CrmRecord[] {
  const parsed = JSON.parse(content) as unknown;

  if (Array.isArray(parsed)) {
    return parsed as CrmRecord[];
  }

  if (parsed && typeof parsed === 'object' && 'records' in parsed) {
    const records = (parsed as { records?: CrmRecord[] }).records;
    return Array.isArray(records) ? records : [];
  }

  return [];
}

function buildPrompt(rows: Record<string, string>[]): string {
  return [
    'Map these CSV rows into GrowEasy CRM records.',
    'Use only these crm_status values: GOOD_LEAD_FOLLOW_UP, DID_NOT_CONNECT, BAD_LEAD, SALE_DONE.',
    'Use only these data_source values when confident: leads_on_demand, meridian_tower, eden_park, varah_swamy, sarjapur_plots.',
    'If a field is not confidently present, leave it blank instead of guessing.',
    'lead_owner must be a real person name or blank. Never use an email, phone number, company name, or generic label for lead_owner.',
    'data_source must be one of the allowed values above or blank. Do not invent a source.',
    'crm_note should only contain remarks, follow-up notes, or extra contact info that does not fit another field.',
    'Skip any row that lacks both email and mobile number.',
    'created_at must be a valid JavaScript date string.',
    'Return a JSON object in the form {"records": [...] } with one object per kept row.',
    JSON.stringify(rows)
  ].join('\n');
}

export async function extractCrmRecords(rows: Record<string, string>[], batchSize: number): Promise<{ records: CrmRecord[]; batchesProcessed: number }> {
  const batchesProcessed = Math.max(1, Math.ceil(rows.length / batchSize));
  const apiKey = process.env.OPENAI_API_KEY;

  if (!apiKey) {
    return {
      records: fallbackExtract(rows),
      batchesProcessed
    };
  }

  const client = new OpenAI({ apiKey });
  const records: CrmRecord[] = [];

  for (let offset = 0; offset < rows.length; offset += batchSize) {
    const batch = rows.slice(offset, offset + batchSize);
    try {
      const completion = await client.chat.completions.create({
        model: process.env.OPENAI_MODEL ?? 'gpt-4o-mini',
        temperature: 0,
        response_format: { type: 'json_object' },
        messages: [
          {
            role: 'system',
            content: 'You extract CRM records from messy CSV rows and return only valid JSON.'
          },
          {
            role: 'user',
            content: buildPrompt(batch)
          }
        ]
      });

      const content = completion.choices[0]?.message?.content ?? '[]';
      const parsed = parseJsonArray(content).map((record) => normalizeExtractedRecord(record));
      records.push(...parsed.filter((record) => record.email || record.mobile_without_country_code));
    } catch {
      records.push(...fallbackExtract(batch).map((record) => normalizeExtractedRecord(record)));
    }
  }

  return { records, batchesProcessed };
}
