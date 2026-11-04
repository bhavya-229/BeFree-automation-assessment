import type { StatementRecord, StatementSummary, NormalizedTransaction } from '../types';

const API_BASE = '/api/v1';

export class ApiError extends Error {
  code?: string;
  status?: number;
  details?: any;

  constructor(message: string, code?: string, status?: number, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export async function uploadStatement(file: File, password?: string): Promise<StatementRecord> {
  const formData = new FormData();
  formData.append('file', file);
  if (password) {
    formData.append('password', password);
  }

  const res = await fetch(`${API_BASE}/statements`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const code = errorData.detail?.code || errorData.code;
    const message = errorData.detail?.detail || errorData.detail?.message || 'Upload failed.';
    throw new ApiError(message, code, res.status, errorData);
  }

  return res.json();
}

export async function listStatements(): Promise<StatementSummary[]> {
  const res = await fetch(`${API_BASE}/statements`);
  if (!res.ok) {
    throw new Error('Failed to list statements.');
  }
  return res.json();
}

export async function deleteStatement(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/statements/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete statement.');
  }
}

export async function getStatement(id: string): Promise<StatementRecord> {
  const res = await fetch(`${API_BASE}/statements/${id}`);
  if (!res.ok) {
    throw new Error('Failed to load statement.');
  }
  return res.json();
}

export async function updateTransactionCategory(
  statementId: string,
  transactionId: string,
  category: string
): Promise<NormalizedTransaction> {
  const res = await fetch(`${API_BASE}/statements/${statementId}/transactions/${transactionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category }),
  });

  if (!res.ok) {
    throw new Error('Failed to update category.');
  }

  return res.json();
}

export function getExportCsvUrl(statementId: string): string {
  return `${API_BASE}/statements/${statementId}/export/csv`;
}

export function getExportXlsxUrl(statementId: string): string {
  return `${API_BASE}/statements/${statementId}/export/xlsx`;
}

export async function loadSampleStatement(
  sampleKey: string,
  password?: string
): Promise<StatementRecord> {
  const url = password
    ? `${API_BASE}/statements/samples/${sampleKey}?password=${encodeURIComponent(password)}`
    : `${API_BASE}/statements/samples/${sampleKey}`;

  const res = await fetch(url, {
    method: 'POST',
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const code = errorData.detail?.code || errorData.code;
    const message = errorData.detail?.detail || errorData.detail?.message || 'Failed to load sample statement.';
    throw new ApiError(message, code, res.status, errorData);
  }

  return res.json();
}

export function getSampleDownloadUrl(sampleKey: string): string {
  return `${API_BASE}/statements/samples/${sampleKey}/download`;
}

