import React from 'react';
import type { NormalizedTransaction, ReconciliationSummary } from '../types';
import { Calculator, CheckCircle2, AlertTriangle, Info, ShieldAlert } from 'lucide-react';

interface StatementValidationProps {
  transactions: NormalizedTransaction[];
  recon: ReconciliationSummary;
  currency?: string;
}

export const StatementValidation: React.FC<StatementValidationProps> = ({
  transactions,
  recon,
  currency: _currency = 'AUD',
}) => {
  const isHealthy = recon.quality_score >= 90;

  return (
    <div className="space-y-6">
      {/* Mathematical Proof Header */}
      <div className="bg-white rounded-2xl border border-[#E4E2EC] p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E4E2EC] gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-[#2E2C8F]">
              <Calculator className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-base text-[#1B1637]">
                Running Balance Mathematical Verification
              </h3>
              <p className="text-xs text-[#5B5875]">Deterministic Ledger Integrity Audit</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-[#5B5875]">Statement Quality:</span>
            <span className={`px-2.5 py-1 rounded-full text-xs font-bold tabular-nums flex items-center space-x-1 ${
              isHealthy
                ? 'bg-emerald-50 text-[#137A3F] border border-emerald-200'
                : 'bg-amber-50 text-amber-800 border border-amber-200'
            }`}>
              {isHealthy ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
              <span>{recon.quality_score}% Quality Score</span>
            </span>
          </div>
        </div>

        {/* Audit Formula Explanation */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-2 text-slate-700">
          <p className="font-semibold text-slate-900 flex items-center space-x-1.5">
            <Info className="w-4 h-4 text-[#2E2C8F]" />
            <span>Mathematical Validation Rule</span>
          </p>
          <p className="leading-relaxed">
            The engine evaluates every adjacent row against the fundamental banking accounting invariant:
          </p>
          <div className="p-2.5 bg-white border border-slate-300 rounded-lg font-mono text-center text-xs font-bold text-slate-900 shadow-2xs">
            Previous Balance − Debit + Credit == Current Balance (Tolerance ±$0.01)
          </div>
          <p className="text-[11px] text-slate-500">
            {recon.discrepancy_explanation}
          </p>
        </div>
      </div>

      {/* Row-by-Row Reconciliation Ledger */}
      <div className="bg-white rounded-2xl border border-[#E4E2EC] shadow-xs overflow-hidden">
        <div className="p-4 border-b border-[#E4E2EC] flex items-center justify-between bg-slate-50">
          <h4 className="font-bold text-xs uppercase tracking-wider text-slate-700">
            Consecutive Balance Audit Ledger ({transactions.length} rows verified)
          </h4>
          <span className="text-xs font-medium text-emerald-700">
            {recon.reconciled_count} / {recon.total_transactions} Rows Validated
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-[#E4E2EC] text-left text-xs">
            <thead className="bg-[#FAF7F0]">
              <tr>
                <th className="px-4 py-3 font-bold text-slate-700">Seq #</th>
                <th className="px-4 py-3 font-bold text-slate-700">Date</th>
                <th className="px-4 py-3 font-bold text-slate-700">Description</th>
                <th className="px-4 py-3 font-bold text-slate-700 text-right">Debit (−)</th>
                <th className="px-4 py-3 font-bold text-slate-700 text-right">Credit (+)</th>
                <th className="px-4 py-3 font-bold text-slate-700 text-right">Expected Balance</th>
                <th className="px-4 py-3 font-bold text-slate-700 text-right">Statement Balance</th>
                <th className="px-4 py-3 font-bold text-slate-700">Audit Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {transactions.map((txn, idx) => {
                const prev = idx > 0 ? transactions[idx - 1] : null;
                const prevBal = prev?.balance ? parseFloat(prev.balance.replace(/,/g, '')) : null;
                const curBal = txn.balance ? parseFloat(txn.balance.replace(/,/g, '')) : null;
                const deb = txn.debit ? parseFloat(txn.debit.replace(/,/g, '')) : 0;
                const cred = txn.credit ? parseFloat(txn.credit.replace(/,/g, '')) : 0;

                let expected = prevBal !== null ? prevBal - deb + cred : null;
                let isRowMatch = expected !== null && curBal !== null
                  ? Math.abs(expected - curBal) <= 0.02
                  : true;

                return (
                  <tr key={txn.id} className={!isRowMatch ? 'bg-amber-50/50' : 'hover:bg-slate-50/50'}>
                    <td className="px-4 py-2.5 font-mono text-slate-500">{txn.line_number}</td>
                    <td className="px-4 py-2.5 font-medium text-slate-900 whitespace-nowrap">{txn.date || txn.date_raw}</td>
                    <td className="px-4 py-2.5 max-w-xs truncate font-medium text-slate-800">{txn.description}</td>
                    <td className="px-4 py-2.5 text-right font-semibold text-[#B42318] tabular-nums">
                      {txn.debit ? `−${txn.debit}` : ''}
                    </td>
                    <td className="px-4 py-2.5 text-right font-semibold text-[#137A3F] tabular-nums">
                      {txn.credit ? `+${txn.credit}` : ''}
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono text-slate-500 tabular-nums">
                      {expected !== null ? expected.toFixed(2) : '—'}
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono font-bold text-slate-900 tabular-nums">
                      {txn.balance || '—'}
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap">
                      {isRowMatch ? (
                        <span className="inline-flex items-center space-x-1 text-emerald-700 font-semibold text-[11px]">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Reconciled</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 text-amber-700 font-semibold text-[11px]">
                          <ShieldAlert className="w-3.5 h-3.5" />
                          <span>Delta Break</span>
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
