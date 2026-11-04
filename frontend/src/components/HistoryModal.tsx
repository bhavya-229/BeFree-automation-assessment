import React, { useEffect, useState } from 'react';
import { Database, Calendar, FileText, CheckCircle2, AlertTriangle, Trash2, ArrowUpRight, X, Loader2 } from 'lucide-react';
import { listStatements, getStatement, deleteStatement } from '../lib/api';
import type { StatementSummary, StatementRecord } from '../types';

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectStatement: (record: StatementRecord) => void;
  activeStatementId?: string;
}

export const HistoryModal: React.FC<HistoryModalProps> = ({
  isOpen,
  onClose,
  onSelectStatement,
  activeStatementId,
}) => {
  const [statements, setStatements] = useState<StatementSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchStatements = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listStatements();
      setStatements(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch statement history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchStatements();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleOpen = async (id: string) => {
    setLoadingId(id);
    try {
      const record = await getStatement(id);
      onSelectStatement(record);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to open statement.');
    } finally {
      setLoadingId(null);
    }
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!window.confirm('Delete this statement and its audit ledger from SQLite?')) return;
    setDeletingId(id);
    try {
      await deleteStatement(id);
      setStatements((prev) => prev.filter((s) => s.id !== id));
    } catch (err: any) {
      setError(err.message || 'Failed to delete statement.');
    } finally {
      setDeletingId(null);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (isoString: string): string => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 max-h-[85vh] flex flex-col space-y-4 animate-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-[#2E2C8F]">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-base text-[#1B1637]">
                Statement History & SQLite Database
              </h3>
              <p className="text-xs text-[#5B5875]">
                Persistent sessions saved in SQLite (WAL Mode) • Zero data loss across server restarts
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto pr-1 space-y-3">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-800 text-xs">
              {error}
            </div>
          )}

          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center space-y-2 text-[#5B5875]">
              <Loader2 className="w-6 h-6 animate-spin text-[#2E2C8F]" />
              <p className="text-xs">Querying SQLite database...</p>
            </div>
          ) : statements.length === 0 ? (
            <div className="py-12 text-center text-[#5B5875] space-y-2">
              <FileText className="w-10 h-10 text-slate-300 mx-auto" />
              <p className="font-bold text-sm text-[#1B1637]">No statements processed yet</p>
              <p className="text-xs max-w-sm mx-auto">
                Upload a bank statement PDF or run one of the pre-bundled demo fixtures to persist it in SQLite.
              </p>
            </div>
          ) : (
            <div className="space-y-2.5">
              {statements.map((stmt) => {
                const isActive = stmt.id === activeStatementId;
                return (
                  <div
                    key={stmt.id}
                    onClick={() => handleOpen(stmt.id)}
                    className={`border rounded-xl p-3.5 flex items-center justify-between cursor-pointer transition ${
                      isActive
                        ? 'border-[#2E2C8F] bg-indigo-50/50 shadow-2xs'
                        : 'border-[#E4E2EC] bg-white hover:border-[#2E2C8F] hover:shadow-xs'
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-xs text-[#1B1637]">{stmt.filename}</span>
                        {isActive && (
                          <span className="text-[10px] font-extrabold px-1.5 py-0.2 rounded bg-[#2E2C8F] text-white">
                            ACTIVE
                          </span>
                        )}
                        <span className="text-[10px] font-bold px-1.5 py-0.2 rounded border bg-slate-50 border-slate-200 text-slate-700">
                          {stmt.currency}
                        </span>
                        {stmt.bank_name && (
                          <span className="text-[10px] font-semibold text-[#5B5875] hidden sm:inline">
                            • {stmt.bank_name}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center space-x-3 text-[11px] text-[#5B5875]">
                        <span className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3 text-slate-400" />
                          <span>{formatDate(stmt.created_at)}</span>
                        </span>
                        <span>•</span>
                        <span>{stmt.transaction_count} transactions</span>
                        <span>•</span>
                        <span>{formatFileSize(stmt.file_size_bytes)}</span>
                        <span>•</span>
                        <span className="flex items-center space-x-1">
                          {stmt.statement_reconciled ? (
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          ) : (
                            <AlertTriangle className="w-3 h-3 text-amber-500" />
                          )}
                          <span className={stmt.statement_reconciled ? 'text-emerald-700 font-bold' : 'text-amber-700'}>
                            {stmt.quality_score.toFixed(0)}% Score
                          </span>
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-1">
                      <button
                        type="button"
                        disabled={loadingId === stmt.id}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpen(stmt.id);
                        }}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 bg-[#FAF7F0] hover:bg-indigo-50 border border-[#E4E2EC] text-[#2E2C8F] rounded-lg text-xs font-bold transition"
                      >
                        {loadingId === stmt.id ? (
                          <Loader2 className="w-3 h-3 animate-spin" />
                        ) : (
                          <ArrowUpRight className="w-3 h-3" />
                        )}
                        <span>Open</span>
                      </button>

                      <button
                        type="button"
                        disabled={deletingId === stmt.id}
                        onClick={(e) => handleDelete(e, stmt.id)}
                        className="p-1.5 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition"
                        title="Delete statement"
                      >
                        {deletingId === stmt.id ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin text-red-600" />
                        ) : (
                          <Trash2 className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-[#5B5875]">
          <span>Database: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-[11px] text-slate-700 font-mono">data/statements.db</code></span>
          <button
            type="button"
            onClick={onClose}
            className="px-3.5 py-1.5 border border-slate-200 rounded-xl font-semibold text-slate-700 hover:bg-slate-50 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
