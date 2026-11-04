import React, { useState } from 'react';
import { ShieldCheck, BookOpen, Layers, HelpCircle, X, CheckCircle2, Lock, Database } from 'lucide-react';
import { HistoryModal } from './HistoryModal';
import type { StatementRecord } from '../types';

interface HeaderProps {
  activeView: 'workspace' | 'rules' | 'help';
  onViewChange: (view: 'workspace' | 'rules' | 'help') => void;
  onSelectStatement?: (record: StatementRecord) => void;
  activeStatementId?: string;
}

export const Header: React.FC<HeaderProps> = ({
  onViewChange,
  onSelectStatement,
  activeStatementId,
}) => {
  const [modalOpen, setModalOpen] = useState<'rules' | 'help' | 'history' | null>(null);

  return (
    <>
      <header className="bg-white border-b border-[#E4E2EC] sticky top-0 z-30 shadow-2xs">
        {/* 4px Signature Fintech Gradient Bar */}
        <div className="h-1 w-full bg-gradient-to-r from-[#F9A03F] via-[#F0568A] via-[#4040D6] to-[#24124F]" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Brand Logo & Wordmark */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onViewChange('workspace')}>
            <div className="w-10 h-10 rounded-xl bg-[#FAF7F0] border border-[#E4E2EC] flex items-center justify-center text-[#2E2C8F] font-black text-xl shadow-xs">
              BF
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg text-[#1B1637] tracking-tight">
                  Bank Statement Processor
                </span>
                <span className="hidden md:inline-flex items-center text-[10px] font-bold bg-[#FAF7F0] text-[#2E2C8F] px-2 py-0.5 rounded border border-[#E4E2EC]">
                  PROTOTYPE
                </span>
              </div>
              <p className="text-xs text-[#5B5875]">Document-AI & Non-LLM Transaction Intelligence</p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            <button
              type="button"
              onClick={() => setModalOpen('history')}
              className="inline-flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg text-[#2E2C8F] bg-indigo-50/70 border border-indigo-100 hover:bg-indigo-100/70 transition shadow-2xs"
            >
              <Database className="w-3.5 h-3.5 text-[#2E2C8F]" />
              <span>History</span>
            </button>

            <button
              type="button"
              onClick={() => setModalOpen('rules')}
              className="inline-flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg text-[#5B5875] hover:text-[#1B1637] hover:bg-slate-100 transition"
            >
              <Layers className="w-4 h-4 text-[#2E2C8F]" />
              <span className="hidden sm:inline">Taxonomy & Rules</span>
            </button>

            <button
              type="button"
              onClick={() => setModalOpen('help')}
              className="inline-flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg text-[#5B5875] hover:text-[#1B1637] hover:bg-slate-100 transition"
            >
              <HelpCircle className="w-4 h-4 text-[#2E2C8F]" />
              <span className="hidden sm:inline">Standards & Audit</span>
            </button>

            {/* Privacy Badge */}
            <div className="hidden lg:flex items-center space-x-2 text-xs font-semibold text-[#137A3F] bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-200">
              <ShieldCheck className="w-4 h-4 text-[#137A3F]" />
              <span>Zero-LLM • 100% Deterministic & Private</span>
            </div>
          </div>
        </div>
      </header>

      {/* History Modal */}
      <HistoryModal
        isOpen={modalOpen === 'history'}
        onClose={() => setModalOpen(null)}
        onSelectStatement={(rec) => {
          if (onSelectStatement) {
            onSelectStatement(rec);
            onViewChange('workspace');
          }
        }}
        activeStatementId={activeStatementId}
      />

      {/* Rules & Taxonomy Modal */}
      {modalOpen === 'rules' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Layers className="w-5 h-5 text-[#2E2C8F]" />
                <h3 className="font-bold text-lg text-slate-900">Dual-Engine Classification Architecture</h3>
              </div>
              <button onClick={() => setModalOpen(null)} className="p-1 text-slate-400 hover:text-slate-600 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-4 space-y-4 text-sm text-slate-600 leading-relaxed">
              <div className="p-3 bg-indigo-50/70 border border-indigo-100 rounded-xl text-indigo-950 text-xs">
                <strong>Strict Privacy Constraint:</strong> No Generative AI or LLM API is used anywhere. Classification executes entirely in-memory using deterministic rules and calibrated scikit-learn models.
              </div>

              <div>
                <h4 className="font-semibold text-slate-900 text-sm">Classification Decision Cascade:</h4>
                <ol className="list-decimal pl-5 mt-1 space-y-1 text-xs">
                  <li><strong>Manual Override (1.00 Conf):</strong> Human user corrections always win and are preserved.</li>
                  <li><strong>Heuristic Rules Engine (≥ 0.80 Conf):</strong> High-precision inverted keyword index matching AU/UK merchants and banking channels.</li>
                  <li><strong>Calibrated Logistic Regression (≥ 0.60 Conf):</strong> TF-IDF character & word n-grams trained on synthetic banking patterns.</li>
                  <li><strong>Review Queue (&lt; 0.60 Conf):</strong> Low-confidence or ambiguous items are flagged for human audit.</li>
                </ol>
              </div>

              <div>
                <h4 className="font-semibold text-slate-900 text-sm">Standard Financial Taxonomy:</h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2 text-xs">
                  {[
                    'Salary & Wages', 'Groceries', 'Dining & Restaurants', 'Utilities & Bills',
                    'Transport & Travel', 'Rent & Housing', 'Shopping & Retail', 'Healthcare & Pharmacy',
                    'Interest & Investments', 'Refunds & Cashbacks', 'Entertainment & Subscriptions',
                    'Loan & Credit Payments', 'Fees & Charges', 'Cash Withdrawal', 'Transfers In',
                    'Transfers Out', 'Insurance', 'Other Income', 'Other / Unclassified'
                  ].map((cat) => (
                    <div key={cat} className="p-2 bg-slate-50 border border-slate-200 rounded-lg font-medium text-slate-700">
                      {cat}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={() => setModalOpen(null)}
                className="px-4 py-2 bg-[#2E2C8F] text-white text-xs font-semibold rounded-lg hover:bg-[#25237A]"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Help & Standards Modal */}
      {modalOpen === 'help' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <HelpCircle className="w-5 h-5 text-[#2E2C8F]" />
                <h3 className="font-bold text-lg text-slate-900">Engineering Standards & Security</h3>
              </div>
              <button onClick={() => setModalOpen(null)} className="p-1 text-slate-400 hover:text-slate-600 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-4 space-y-4 text-sm text-slate-600 leading-relaxed">
              <div className="border border-slate-200 rounded-xl p-3">
                <h4 className="font-semibold text-slate-900 text-xs flex items-center space-x-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Mathematical Reconciliation Formula</span>
                </h4>
                <p className="text-xs text-slate-600 mt-1">
                  For every consecutive row, the system rigorously validates:
                  <code className="block bg-slate-100 p-1.5 rounded mt-1 font-mono text-[11px] text-slate-800">
                    Previous Balance − Debit + Credit == Current Balance (±0.01)
                  </code>
                  Discrepancies are flagged as <code>BALANCE_MISMATCH</code> without silently modifying values.
                </p>
              </div>

              <div className="border border-slate-200 rounded-xl p-3">
                <h4 className="font-semibold text-slate-900 text-xs flex items-center space-x-1.5">
                  <Lock className="w-4 h-4 text-blue-600" />
                  <span>OWASP Formula Injection Defense</span>
                </h4>
                <p className="text-xs text-slate-600 mt-1">
                  Exported CSV and Excel files sanitize all text cells starting with <code>=</code>, <code>+</code>, <code>-</code>, or <code>@</code> with a leading apostrophe (<code>'</code>) to prevent DDE/spreadsheet execution attacks.
                </p>
              </div>

              <div className="border border-slate-200 rounded-xl p-3">
                <h4 className="font-semibold text-slate-900 text-xs flex items-center space-x-1.5">
                  <BookOpen className="w-4 h-4 text-purple-600" />
                  <span>Supported Statement Layouts</span>
                </h4>
                <p className="text-xs text-slate-600 mt-1">
                  Pre-configured profiles for Australian banks (CommBank BSB, Westpac, ANZ) and UK banks (Barclays Sort Code, HSBC, NatWest) plus universal generic column fallback.
                </p>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={() => setModalOpen(null)}
                className="px-4 py-2 bg-[#2E2C8F] text-white text-xs font-semibold rounded-lg hover:bg-[#25237A]"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
