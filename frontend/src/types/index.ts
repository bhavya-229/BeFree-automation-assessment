export type PageType = 'DIGITAL' | 'SCANNED' | 'HYBRID';
export type DocType = 'DIGITAL' | 'SCANNED' | 'MIXED';
export type ClassificationSource = 'RULE' | 'ML' | 'MANUAL' | 'UNCLASSIFIED';

export interface PageTypeMetrics {
  page_number: number;
  page_type: PageType;
  meaningful_text_count: number;
  total_char_count: number;
  garbage_char_ratio: number;
  image_count: number;
  image_area_ratio: number;
  width: number;
  height: number;
  reason: string;
}

export interface DocumentTypeReport {
  doc_type: DocType;
  total_pages: number;
  digital_page_count: number;
  scanned_page_count: number;
  hybrid_page_count: number;
  pages: PageTypeMetrics[];
  reason: string;
}

export interface NormalizedTransaction {
  id: string;
  statement_id?: string;
  line_number: number;
  page_number: number;
  date: string | null;
  date_raw: string;
  value_date?: string | null;
  description: string;
  description_raw: string;
  ref_no?: string | null;
  channel?: string | null;
  counterparty?: string | null;
  debit: string | null;
  credit: string | null;
  amount: string | null;
  balance: string | null;
  currency: string;
  raw_debit?: string | null;
  raw_credit?: string | null;
  raw_balance?: string | null;
  category: string;
  subcategory?: string | null;
  category_source: ClassificationSource;
  category_confidence: number;
  rule_id?: string | null;
  ml_top3?: Array<{ category: string; probability: number }>;
  user_edited: boolean;
  flags: string[];
  row_confidence: number;
}

export interface ReconciliationSummary {
  total_transactions: number;
  reconciled_count: number;
  mismatch_count: number;
  quality_score: number;
  total_debits: string;
  total_credits: string;
  net_movement: string;
  opening_balance?: string | null;
  closing_balance?: string | null;
  statement_reconciled: boolean;
  discrepancy_explanation: string;
}

export interface StatementMetadata {
  bank_name?: string;
  account_name?: string;
  account_number?: string;
  account_identifier_type?: string;
  sort_code_or_bsb?: string;
  statement_period_start?: string;
  statement_period_end?: string;
  currency?: string;
  opening_balance?: string;
  closing_balance?: string;
}

export interface StatementRecord {
  id: string;
  filename: string;
  sha256: string;
  file_size_bytes: number;
  page_count: number;
  doc_type_report: DocumentTypeReport;
  reconciliation_summary: ReconciliationSummary;
  transactions: NormalizedTransaction[];
  metadata?: StatementMetadata;
  created_at: string;
}
