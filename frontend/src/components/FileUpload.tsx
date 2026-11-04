import React, { useState, useRef, useEffect } from 'react';
import { UploadCloud, AlertCircle, Loader2, Sparkles, FileText, ShieldCheck, Cpu, Calculator, FileSpreadsheet, Download, Lock, CheckCircle2, Clock, ArrowUpRight, Layers } from 'lucide-react';
import { uploadStatement, loadSampleStatement, getSampleDownloadUrl, ApiError } from '../lib/api';
import { PasswordDialog } from './PasswordDialog';
import type { StatementRecord } from '../types';

interface FileUploadProps {
  onUploadSuccess: (record: StatementRecord) => void;
}

export interface BatchQueueItem {
  id: string;
  file: File;
  status: 'pending' | 'processing' | 'done' | 'error' | 'encrypted';
  errorMessage?: string;
  record?: StatementRecord;
}

type SampleKey = 'cba' | 'barclays' | 'westpac' | 'sbi' | 'encrypted' | 'au100';

interface SampleOption {
  key: SampleKey;
  label: string;
  country: string;
  currency: string;
  badgeColor: string;
  hint?: string;
}

const SAMPLE_OPTIONS: SampleOption[] = [
  { key: 'au100', label: 'AU 100 Scanned (OCR)', country: 'AU', currency: 'AUD', badgeColor: 'text-indigo-700 bg-indigo-50 border-indigo-200', hint: '100 Txns • 3 Pages' },
  { key: 'cba', label: 'CommBank', country: 'AU', currency: 'AUD', badgeColor: 'text-amber-700 bg-amber-50 border-amber-200' },
  { key: 'barclays', label: 'Barclays', country: 'UK', currency: 'GBP', badgeColor: 'text-blue-700 bg-blue-50 border-blue-200' },
  { key: 'westpac', label: 'Westpac', country: 'AU', currency: 'AUD', badgeColor: 'text-rose-700 bg-rose-50 border-rose-200' },
  { key: 'sbi', label: 'SBI', country: 'IN', currency: 'INR', badgeColor: 'text-emerald-700 bg-emerald-50 border-emerald-200' },
  { key: 'encrypted', label: 'Encrypted CBA', country: 'AU', currency: 'AUD', badgeColor: 'text-purple-700 bg-purple-50 border-purple-200', hint: 'Pass: befree2026' },
];

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingSample, setLoadingSample] = useState<SampleKey | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [uploadStage, setUploadStage] = useState<string>('Ready');
  const [slowLoading, setSlowLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let timer: any;
    if (isLoading || loadingSample) {
      timer = setTimeout(() => {
        setSlowLoading(true);
      }, 5000);
    } else {
      setSlowLoading(false);
    }
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [isLoading, loadingSample]);

  // Batch Queue State
  const [batchQueue, setBatchQueue] = useState<BatchQueueItem[]>([]);
  const [batchProcessing, setBatchProcessing] = useState(false);

  // Password Dialog State
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [pendingBatchItemId, setPendingBatchItemId] = useState<string | null>(null);
  const [pendingSampleKey, setPendingSampleKey] = useState<SampleKey | null>(null);
  const [passwordFilename, setPasswordFilename] = useState<string>('');

  const handleFiles = async (files: File[]) => {
    const validFiles = files.filter((f) => f.name.toLowerCase().endsWith('.pdf'));
    if (validFiles.length === 0) {
      setErrorMessage('Please upload valid PDF documents.');
      return;
    }

    if (validFiles.length === 1) {
      handleFile(validFiles[0]);
      return;
    }

    // Initialize Batch Queue
    setErrorMessage(null);
    const initialItems: BatchQueueItem[] = validFiles.map((file, idx) => ({
      id: `${Date.now()}-${idx}`,
      file,
      status: 'pending',
    }));

    setBatchQueue(initialItems);
    setBatchProcessing(true);

    // Process items in sequence
    for (let i = 0; i < initialItems.length; i++) {
      const item = initialItems[i];
      setBatchQueue((prev) =>
        prev.map((it) => (it.id === item.id ? { ...it, status: 'processing' } : it))
      );

      try {
        const record = await uploadStatement(item.file);
        setBatchQueue((prev) =>
          prev.map((it) => (it.id === item.id ? { ...it, status: 'done', record } : it))
        );
      } catch (err: any) {
        if (err instanceof ApiError && (err.code === 'PDF_ENCRYPTED' || err.code === 'WRONG_PASSWORD')) {
          setBatchQueue((prev) =>
            prev.map((it) =>
              it.id === item.id ? { ...it, status: 'encrypted', errorMessage: err.message } : it
            )
          );
        } else {
          setBatchQueue((prev) =>
            prev.map((it) =>
              it.id === item.id ? { ...it, status: 'error', errorMessage: err.message } : it
            )
          );
        }
      }
    }
    setBatchProcessing(false);
  };

  const handleFile = async (file: File, password?: string) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setErrorMessage('Please upload a valid PDF document.');
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      setErrorMessage('File size exceeds the 25 MB limit.');
      return;
    }

    setErrorMessage(null);
    setIsLoading(true);
    setUploadStage(password ? 'Decrypting statement...' : 'Inspecting PDF structure...');

    try {
      const record = await uploadStatement(file, password);
      setPasswordDialogOpen(false);
      setPendingFile(null);
      setPendingBatchItemId(null);
      onUploadSuccess(record);
    } catch (err: any) {
      if (err instanceof ApiError && (err.code === 'PDF_ENCRYPTED' || err.code === 'WRONG_PASSWORD')) {
        setPendingFile(file);
        setPasswordFilename(file.name);
        setPasswordDialogOpen(true);
        if (password) {
          setPasswordError(err.message);
        } else {
          setPasswordError(null);
        }
      } else {
        setErrorMessage(err.message || 'Processing failed. Please check the PDF.');
      }
    } finally {
      setIsLoading(false);
      setPasswordLoading(false);
      setUploadStage('Ready');
    }
  };

  const handleBatchItemUnlock = (item: BatchQueueItem) => {
    setPendingFile(item.file);
    setPendingBatchItemId(item.id);
    setPasswordFilename(item.file.name);
    setPasswordError(null);
    setPasswordDialogOpen(true);
  };

  const handleSample = async (sampleKey: SampleKey, password?: string) => {
    setErrorMessage(null);
    setLoadingSample(sampleKey);
    try {
      const record = await loadSampleStatement(sampleKey, password);
      setPasswordDialogOpen(false);
      setPendingSampleKey(null);
      onUploadSuccess(record);
    } catch (err: any) {
      if (err instanceof ApiError && (err.code === 'PDF_ENCRYPTED' || err.code === 'WRONG_PASSWORD')) {
        setPendingSampleKey(sampleKey);
        setPasswordFilename(`${sampleKey}_statement.pdf (Demo Pass: befree2026)`);
        setPasswordDialogOpen(true);
        if (password) {
          setPasswordError(err.message);
        } else {
          setPasswordError(null);
        }
      } else {
        setErrorMessage(err.message || 'Failed to load demo statement.');
      }
    } finally {
      setLoadingSample(null);
      setPasswordLoading(false);
    }
  };

  const handlePasswordSubmit = async (password: string) => {
    setPasswordLoading(true);
    setPasswordError(null);

    if (pendingFile) {
      try {
        const record = await uploadStatement(pendingFile, password);
        setPasswordDialogOpen(false);
        if (pendingBatchItemId) {
          setBatchQueue((prev) =>
            prev.map((it) => (it.id === pendingBatchItemId ? { ...it, status: 'done', record } : it))
          );
        }
        setPendingFile(null);
        setPendingBatchItemId(null);
        onUploadSuccess(record);
      } catch (err: any) {
        setPasswordError(err.message || 'Decryption failed.');
      } finally {
        setPasswordLoading(false);
      }
    } else if (pendingSampleKey) {
      await handleSample(pendingSampleKey, password);
    }
  };

  const handlePasswordCancel = () => {
    setPasswordDialogOpen(false);
    setPasswordLoading(false);
    setPasswordError(null);
    setPendingFile(null);
    setPendingBatchItemId(null);
    setPendingSampleKey(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto my-8 px-4 sm:px-6 space-y-8">
      {/* Hero Section */}
      <div className="text-center max-w-3xl mx-auto space-y-3">
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-[#2E2C8F] text-xs font-semibold">
          <span>Assessment Prototype</span>
          <span>•</span>
          <span>Fintech Data Engine</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#1B1637] tracking-tight">
          Bank Statement Processor
        </h1>
        <p className="text-sm sm:text-base text-[#5B5875] leading-relaxed">
          Deterministic data extraction, mathematical balance reconciliation, and non-LLM transaction classification across text-based, scanned, and hybrid bank statements.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 shadow-xs ${
          isDragging
            ? 'border-[#2E2C8F] bg-indigo-50/60 scale-[1.01]'
            : 'border-slate-300 hover:border-[#2E2C8F] bg-white hover:shadow-md'
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          multiple
          onChange={(e) => e.target.files && handleFiles(Array.from(e.target.files))}
          accept="application/pdf"
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-[#2E2C8F] shadow-inner">
            {isLoading || batchProcessing ? (
              <Loader2 className="w-8 h-8 animate-spin text-[#2E2C8F]" />
            ) : (
              <UploadCloud className="w-8 h-8 text-[#2E2C8F]" />
            )}
          </div>

          <div className="space-y-1">
            <h3 className="text-lg font-bold text-[#1B1637]">
              {isLoading ? uploadStage : (batchProcessing ? 'Processing Batch Queue...' : 'Upload Bank Statement PDFs')}
            </h3>
            {slowLoading && (
              <p className="text-[11px] font-medium text-amber-800 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-lg max-w-sm mx-auto animate-pulse">
                Cloud backend waking up (Render free tier may take up to 30s on first load)...
              </p>
            )}
            <p className="text-xs text-[#5B5875] max-w-md mx-auto">
              Drag and drop statement files here, or click to browse. Supports single or multi-file batch uploads (digital, scanned, or hybrid multi-page PDFs up to 25 MB).
            </p>
          </div>

          <button
            type="button"
            className="inline-flex items-center px-5 py-2.5 text-xs font-bold rounded-lg text-white bg-[#2E2C8F] hover:bg-[#25237A] shadow-xs transition"
          >
            Select Statement Files (Single or Batch)
          </button>
        </div>
      </div>

      {/* Batch Intake Queue Card */}
      {batchQueue.length > 0 && (
        <div className="bg-white border border-[#E4E2EC] rounded-2xl p-5 shadow-xs space-y-4 animate-in fade-in duration-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-[#2E2C8F]">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <h3 className="font-extrabold text-sm text-[#1B1637]">Batch Processing Queue</h3>
                <p className="text-xs text-[#5B5875]">
                  {batchQueue.filter((i) => i.status === 'done').length} of {batchQueue.length} statements processed
                </p>
              </div>
            </div>
            {batchProcessing ? (
              <div className="flex items-center space-x-2 text-xs font-semibold text-[#2E2C8F]">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing batch...</span>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setBatchQueue([])}
                className="text-xs font-semibold text-slate-500 hover:text-slate-800"
              >
                Clear Queue
              </button>
            )}
          </div>

          <div className="space-y-2">
            {batchQueue.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-3 rounded-xl border border-slate-100 bg-slate-50/60 hover:bg-white hover:border-[#2E2C8F] transition"
              >
                <div className="flex items-center space-x-3">
                  <FileText className="w-4 h-4 text-slate-400" />
                  <div>
                    <p className="text-xs font-bold text-[#1B1637]">{item.file.name}</p>
                    <p className="text-[10px] text-[#5B5875]">{(item.file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {item.status === 'pending' && (
                    <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                      <Clock className="w-3 h-3" />
                      <span>Queued</span>
                    </span>
                  )}
                  {item.status === 'processing' && (
                    <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full">
                      <Loader2 className="w-3 h-3 animate-spin" />
                      <span>Extracting...</span>
                    </span>
                  )}
                  {item.status === 'encrypted' && (
                    <button
                      type="button"
                      onClick={() => handleBatchItemUnlock(item)}
                      className="inline-flex items-center space-x-1 text-[11px] font-bold text-purple-700 bg-purple-50 hover:bg-purple-100 px-2.5 py-1 rounded-full border border-purple-200"
                    >
                      <Lock className="w-3 h-3" />
                      <span>Unlock Password</span>
                    </button>
                  )}
                  {item.status === 'done' && item.record && (
                    <div className="flex items-center space-x-2">
                      <span className="inline-flex items-center space-x-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>{item.record.transactions.length} Txns • {item.record.reconciliation_summary.quality_score.toFixed(0)}% Score</span>
                      </span>
                      <button
                        type="button"
                        onClick={() => onUploadSuccess(item.record!)}
                        className="inline-flex items-center space-x-1 text-xs font-bold text-white bg-[#2E2C8F] hover:bg-[#25237A] px-3 py-1 rounded-lg transition"
                      >
                        <span>Open</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                  {item.status === 'error' && (
                    <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-red-700 bg-red-50 px-2.5 py-0.5 rounded-full border border-red-200">
                      <AlertCircle className="w-3 h-3 text-red-600" />
                      <span>{item.errorMessage || 'Failed'}</span>
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Demo Statement Selector & Direct Downloads */}
      <div className="bg-[#FAF7F0] border border-[#E4E2EC] rounded-2xl p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-[#1B1637] text-xs font-bold">
            <Sparkles className="w-4 h-4 text-amber-500 flex-shrink-0" />
            <span>Test with Pre-bundled Statement Datasets (AU • UK • IN):</span>
          </div>
          <span className="text-[11px] text-[#5B5875] hidden sm:inline">
            Click to process instantly or download the raw PDF to test drag & drop
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {SAMPLE_OPTIONS.map((item) => (
            <div
              key={item.key}
              className="bg-white border border-[#E4E2EC] rounded-xl p-3 flex flex-col justify-between shadow-2xs hover:border-[#2E2C8F] transition"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-1.5 flex-wrap gap-y-1">
                  {item.key === 'encrypted' && <Lock className="w-3.5 h-3.5 text-purple-600 flex-shrink-0" />}
                  <span className="font-extrabold text-xs text-[#1B1637]">{item.label}</span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border ${item.badgeColor}`}>
                    {item.country} • {item.currency}
                  </span>
                </div>
                {item.hint && (
                  <p className="text-[10px] font-mono font-semibold text-purple-700 bg-purple-50/80 px-1.5 py-0.5 rounded w-fit">
                    {item.hint}
                  </p>
                )}
              </div>

              <div className="flex items-center space-x-2 pt-2 border-t border-slate-100 mt-2">
                <button
                  type="button"
                  disabled={loadingSample !== null}
                  onClick={() => handleSample(item.key)}
                  className="text-[11px] font-bold text-[#2E2C8F] hover:underline flex items-center space-x-1 disabled:opacity-50"
                >
                  {loadingSample === item.key ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <FileText className="w-3 h-3" />
                  )}
                  <span>Run in App</span>
                </button>
                <span className="text-slate-300">|</span>
                <a
                  href={getSampleDownloadUrl(item.key)}
                  download
                  className="text-[11px] font-bold text-slate-500 hover:text-slate-900 flex items-center space-x-1"
                  title={`Download ${item.label} PDF`}
                >
                  <Download className="w-3 h-3" />
                  <span>PDF</span>
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-start space-x-3 text-red-800 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-red-600" />
          <div>
            <p className="font-bold text-xs uppercase tracking-wider">Error Processing File</p>
            <p className="text-xs mt-0.5">{errorMessage}</p>
          </div>
        </div>
      )}

      {/* 4 Core Architectural Capabilities */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4">
        <div className="bg-white p-4 rounded-xl border border-[#E4E2EC] shadow-2xs space-y-2">
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center font-bold">
            <Cpu className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-xs text-[#1B1637]">Page-Level Inspector</h4>
          <p className="text-xs text-[#5B5875] leading-normal">
            Direct digital text parsing for clean pages; OpenCV CLAHE & Tesseract OCR only when scanned or font-corrupted.
          </p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-[#E4E2EC] shadow-2xs space-y-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold">
            <Calculator className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-xs text-[#1B1637]">Mathematical Proof</h4>
          <p className="text-xs text-[#5B5875] leading-normal">
            Consecutive balance equation verification (<span className="font-mono text-[11px]">B<sub>t-1</sub> − D + C = B<sub>t</sub></span>) with bounded auto-repair without fabricating amounts.
          </p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-[#E4E2EC] shadow-2xs space-y-2">
          <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center font-bold">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-xs text-[#1B1637]">Non-LLM Intelligence</h4>
          <p className="text-xs text-[#5B5875] leading-normal">
            Deterministic rules engine (≥ 0.80) + calibrated Logistic Regression (≥ 0.60). Zero cloud APIs, 100% private.
          </p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-[#E4E2EC] shadow-2xs space-y-2">
          <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center font-bold">
            <FileSpreadsheet className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-xs text-[#1B1637]">Formula-Safe Export</h4>
          <p className="text-xs text-[#5B5875] leading-normal">
            Neutralizes spreadsheet injection attacks with leading apostrophes. Multi-tab Excel (.xlsx) and UTF-8 BOM CSV.
          </p>
        </div>
      </div>

      <PasswordDialog
        isOpen={passwordDialogOpen}
        isLoading={passwordLoading}
        filename={passwordFilename}
        errorMessage={passwordError}
        onSubmit={handlePasswordSubmit}
        onCancel={handlePasswordCancel}
      />
    </div>
  );
};
