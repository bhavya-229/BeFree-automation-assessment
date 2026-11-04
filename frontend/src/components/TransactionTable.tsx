import React, { useState } from 'react';
import type { NormalizedTransaction } from '../types';
import { Search, Filter, AlertCircle, CheckCircle, X, Tag } from 'lucide-react';
import { updateTransactionCategory } from '../lib/api';

interface TransactionTableProps {
  statementId: string;
  initialTransactions: NormalizedTransaction[];
  currency?: string;
}

const CATEGORY_OPTIONS = [
  'Salary & Wages',
  'Transfers In',
  'Interest & Investments',
  'Refunds & Cashbacks',
  'Other Income',
  'Groceries',
  'Dining & Restaurants',
  'Transport & Travel',
  'Utilities & Bills',
  'Rent & Housing',
  'Shopping & Retail',
  'Healthcare & Pharmacy',
  'Insurance',
  'Fees & Charges',
  'Loan & Credit Payments',
  'Entertainment & Subscriptions',
  'Cash Withdrawal',
  'Transfers Out',
  'Other / Unclassified',
];

export const TransactionTable: React.FC<TransactionTableProps> = ({
  statementId,
  initialTransactions,
  currency = 'AUD',
}) => {
  const [transactions, setTransactions] = useState<NormalizedTransaction[]>(initialTransactions);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [directionFilter, setDirectionFilter] = useState<'ALL' | 'DEBIT' | 'CREDIT'>('ALL');
  const [onlyNeedsReview, setOnlyNeedsReview] = useState(false);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [selectedRow, setSelectedRow] = useState<NormalizedTransaction | null>(null);

  const currSymbol = currency === 'GBP' ? '£' : '$';

  const handleCategoryChange = async (txnId: string, newCategory: string) => {
    setUpdatingId(txnId);
    try {
      const updated = await updateTransactionCategory(statementId, txnId, newCategory);
      setTransactions((prev) =>
        prev.map((t) => (t.id === txnId ? { ...t, ...updated } : t))
      );
      if (selectedRow?.id === txnId) {
        setSelectedRow((prev) => prev ? { ...prev, ...updated, category: newCategory, category_source: 'MANUAL', category_confidence: 1.0 } : null);
      }
    } catch (err) {
      alert('Failed to update category.');
    } finally {
      setUpdatingId(null);
    }
  };

  const filtered = transactions.filter((t) => {
    if (searchQuery) {
      const q = searchQuery.toUpperCase();
      const matchDesc = t.description.toUpperCase().includes(q);
      const matchRaw = t.description_raw.toUpperCase().includes(q);
      const matchRef = t.ref_no ? t.ref_no.toUpperCase().includes(q) : false;
      if (!matchDesc && !matchRaw && !matchRef) return false;
    }

    if (selectedCategory !== 'ALL' && t.category !== selectedCategory) {
      return false;
    }

    if (directionFilter === 'DEBIT' && !t.debit) return false;
    if (directionFilter === 'CREDIT' && !t.credit) return false;

    if (onlyNeedsReview) {
      const hasReviewFlag =
        t.flags.includes('LOW_CONFIDENCE') ||
        t.flags.includes('BALANCE_MISMATCH') ||
        t.category_source === 'UNCLASSIFIED';
      if (!hasReviewFlag) return false;
    }

    return true;
  });

  return (
    <div className="space-y-4">
      {/* Filter and Search Bar */}
      <div className="bg-white rounded-2xl border border-[#E4E2EC] p-4 shadow-2xs flex flex-col lg:flex-row items-center justify-between gap-4">
        {/* Search */}
        <div className="relative w-full lg:w-96">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-[#5B5875]" />
          <input
            type="text"
            placeholder="Search merchants, narrations, references..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-[#2E2C8F] focus:outline-hidden"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
          {/* Direction Filter Pills */}
          <div className="inline-flex rounded-xl bg-slate-100 p-0.5 border border-slate-200 text-xs font-semibold">
            <button
              type="button"
              onClick={() => setDirectionFilter('ALL')}
              className={`px-3 py-1 rounded-lg transition ${
                directionFilter === 'ALL'
                  ? 'bg-white text-[#1B1637] shadow-2xs'
                  : 'text-[#5B5875] hover:text-[#1B1637]'
              }`}
            >
              All
            </button>
            <button
              type="button"
              onClick={() => setDirectionFilter('DEBIT')}
              className={`px-3 py-1 rounded-lg transition ${
                directionFilter === 'DEBIT'
                  ? 'bg-white text-[#B42318] shadow-2xs'
                  : 'text-[#5B5875] hover:text-[#B42318]'
              }`}
            >
              Debits (Dr)
            </button>
            <button
              type="button"
              onClick={() => setDirectionFilter('CREDIT')}
              className={`px-3 py-1 rounded-lg transition ${
                directionFilter === 'CREDIT'
                  ? 'bg-white text-[#137A3F] shadow-2xs'
                  : 'text-[#5B5875] hover:text-[#137A3F]'
              }`}
            >
              Credits (Cr)
            </button>
          </div>

          {/* Category Filter */}
          <div className="flex items-center space-x-1.5">
            <Filter className="w-3.5 h-3.5 text-[#5B5875]" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="text-xs border border-slate-300 rounded-xl px-3 py-1.5 bg-white focus:ring-2 focus:ring-[#2E2C8F] focus:outline-hidden"
            >
              <option value="ALL">All Categories</option>
              {CATEGORY_OPTIONS.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Needs Review Toggle */}
          <label className="flex items-center space-x-2 cursor-pointer text-xs font-semibold text-[#1B1637] bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-100">
            <input
              type="checkbox"
              checked={onlyNeedsReview}
              onChange={(e) => setOnlyNeedsReview(e.target.checked)}
              className="rounded text-[#2E2C8F] focus:ring-[#2E2C8F]"
            />
            <span>Needs Review</span>
          </label>
        </div>
      </div>

      {/* Main Grid Surface */}
      <div className="bg-white rounded-2xl border border-[#E4E2EC] shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-[#E4E2EC] text-left text-xs">
            <thead className="bg-[#FAF7F0] border-b border-[#E4E2EC]">
              <tr>
                <th scope="col" className="px-4 py-3 font-bold text-[#1B1637]">Date</th>
                <th scope="col" className="px-4 py-3 font-bold text-[#1B1637]">Description & Narration</th>
                <th scope="col" className="px-4 py-3 font-bold text-[#1B1637] text-right">Debit (Dr)</th>
                <th scope="col" className="px-4 py-3 font-bold text-[#1B1637] text-right">Credit (Cr)</th>
                <th scope="col" className="px-4 py-3 font-bold text-[#1B1637] text-right">Balance</th>
                <th scope="col" className="px-4 py-3 font-bold text-[#1B1637]">Category & Audit</th>
                <th scope="col" className="px-4 py-3 font-bold text-[#1B1637]">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-[#5B5875]">
                    No transactions match the specified filters.
                  </td>
                </tr>
              ) : (
                filtered.map((txn) => {
                  const hasWarning =
                    txn.flags.includes('BALANCE_MISMATCH') ||
                    txn.flags.includes('LOW_CONFIDENCE');

                  return (
                    <tr
                      key={txn.id}
                      onClick={() => setSelectedRow(txn)}
                      className={`hover:bg-slate-50/80 cursor-pointer transition-colors ${
                        hasWarning ? 'bg-amber-50/30' : ''
                      } ${selectedRow?.id === txn.id ? 'ring-2 ring-indigo-500 bg-indigo-50/20' : ''}`}
                    >
                      {/* Date */}
                      <td className="px-4 py-3 font-medium text-[#1B1637] whitespace-nowrap">
                        {txn.date || txn.date_raw}
                      </td>

                      {/* Description */}
                      <td className="px-4 py-3 max-w-sm">
                        <div className="font-bold text-[#1B1637] leading-tight">
                          {txn.description}
                        </div>
                        {txn.description_raw !== txn.description && (
                          <div className="text-[11px] text-[#5B5875] mt-0.5 truncate" title={txn.description_raw}>
                            Raw: {txn.description_raw}
                          </div>
                        )}
                        <div className="flex items-center space-x-1.5 mt-1">
                          {txn.channel && (
                            <span className="text-[10px] font-bold bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded">
                              {txn.channel}
                            </span>
                          )}
                          {txn.ref_no && (
                            <span className="text-[10px] font-mono bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded">
                              Ref: {txn.ref_no}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Debit */}
                      <td className="px-4 py-3 text-right tabular-nums whitespace-nowrap font-bold text-[#B42318]">
                        {txn.debit ? `−${currSymbol}${txn.debit}` : ''}
                      </td>

                      {/* Credit */}
                      <td className="px-4 py-3 text-right tabular-nums whitespace-nowrap font-bold text-[#137A3F]">
                        {txn.credit ? `+${currSymbol}${txn.credit}` : ''}
                      </td>

                      {/* Balance */}
                      <td className="px-4 py-3 text-right tabular-nums whitespace-nowrap font-mono font-bold text-[#1B1637]">
                        {txn.balance ? `${currSymbol}${txn.balance}` : ''}
                      </td>

                      {/* Category & Source */}
                      <td className="px-4 py-3 min-w-[220px]" onClick={(e) => e.stopPropagation()}>
                        <div className="space-y-1">
                          <select
                            disabled={updatingId === txn.id}
                            value={txn.category}
                            onChange={(e) => handleCategoryChange(txn.id, e.target.value)}
                            className="w-full text-xs font-semibold border border-slate-300 rounded-lg px-2 py-1 bg-white focus:ring-1 focus:ring-[#2E2C8F] focus:outline-hidden"
                          >
                            {CATEGORY_OPTIONS.map((cat) => (
                              <option key={cat} value={cat}>
                                {cat}
                              </option>
                            ))}
                          </select>

                          <div className="flex items-center space-x-1.5">
                            <span
                              className={`text-[10px] font-bold px-1.5 py-0.2 rounded uppercase tracking-wider ${
                                txn.category_source === 'RULE'
                                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                                  : txn.category_source === 'ML'
                                  ? 'bg-purple-50 text-purple-700 border border-purple-200'
                                  : txn.category_source === 'MANUAL'
                                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                  : 'bg-slate-100 text-slate-700'
                              }`}
                            >
                              {txn.category_source} ({Math.round(txn.category_confidence * 100)}%)
                            </span>
                            {txn.rule_id && (
                              <span className="text-[10px] text-slate-400 font-mono truncate max-w-[90px]" title={txn.rule_id}>
                                {txn.rule_id}
                              </span>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Status / Flags */}
                      <td className="px-4 py-3 whitespace-nowrap">
                        {txn.flags.length === 0 ? (
                          <span className="inline-flex items-center text-xs text-emerald-700 font-semibold space-x-1">
                            <CheckCircle className="w-3.5 h-3.5" />
                            <span>Verified</span>
                          </span>
                        ) : (
                          <div className="flex flex-wrap gap-1">
                            {txn.flags.map((flag) => (
                              <span
                                key={flag}
                                className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center space-x-1 ${
                                  flag === 'BALANCE_MISMATCH'
                                    ? 'bg-red-50 text-red-700 border border-red-200'
                                    : flag === 'LOW_CONFIDENCE'
                                    ? 'bg-amber-50 text-amber-800 border border-amber-200'
                                    : 'bg-blue-50 text-blue-700 border border-blue-200'
                                }`}
                              >
                                <AlertCircle className="w-2.5 h-2.5" />
                                <span>{flag.replace(/_/g, ' ')}</span>
                              </span>
                            ))}
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Row Detail Drawer (Slide-Over Panel) */}
      {selectedRow && (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white shadow-2xl border-l border-slate-200 p-6 flex flex-col justify-between overflow-y-auto animate-in slide-in-from-right duration-200">
          <div className="space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-200">
              <div className="flex items-center space-x-2">
                <Tag className="w-4 h-4 text-[#2E2C8F]" />
                <h3 className="font-extrabold text-sm text-[#1B1637]">
                  Transaction Audit Detail
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedRow(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Main Financial Attributes */}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#5B5875]">Transaction Date:</span>
                <span className="font-bold text-[#1B1637]">{selectedRow.date || selectedRow.date_raw}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-[#5B5875]">Amount:</span>
                <span className={`font-bold tabular-nums ${selectedRow.debit ? 'text-[#B42318]' : 'text-[#137A3F]'}`}>
                  {selectedRow.debit ? `−${currSymbol}${selectedRow.debit} (Debit)` : `+${currSymbol}${selectedRow.credit} (Credit)`}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-[#5B5875]">Resulting Balance:</span>
                <span className="font-mono font-bold text-[#1B1637]">{currSymbol}{selectedRow.balance || '—'}</span>
              </div>
            </div>

            {/* Description Comparison */}
            <div className="space-y-2 text-xs">
              <span className="font-bold uppercase tracking-wider text-[#5B5875]">Extracted Narrations</span>
              <div className="p-3 bg-white border border-slate-200 rounded-xl space-y-2">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">Normalized Description:</span>
                  <p className="font-bold text-slate-800">{selectedRow.description}</p>
                </div>
                <div className="pt-2 border-t border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">Raw Verbatim String:</span>
                  <p className="font-mono text-[11px] text-slate-600 break-all">{selectedRow.description_raw}</p>
                </div>
              </div>
            </div>

            {/* Classification Explainability */}
            <div className="space-y-2 text-xs">
              <span className="font-bold uppercase tracking-wider text-[#5B5875]">Classification Explainability</span>
              <div className="p-3 bg-indigo-50/50 border border-indigo-100 rounded-xl space-y-2 text-slate-800">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold">Assigned Category:</span>
                  <span className="font-bold text-[#2E2C8F]">{selectedRow.category}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold">Classification Engine:</span>
                  <span className="font-mono text-xs font-bold">{selectedRow.category_source}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold">Confidence Score:</span>
                  <span className="font-bold">{Math.round(selectedRow.category_confidence * 100)}%</span>
                </div>
                {selectedRow.rule_id && (
                  <div className="flex items-center justify-between pt-1 border-t border-indigo-100 text-[11px]">
                    <span className="text-slate-500">Matched Rule:</span>
                    <span className="font-mono text-indigo-700 font-semibold">{selectedRow.rule_id}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Payment Rails & Reference */}
            <div className="space-y-2 text-xs">
              <span className="font-bold uppercase tracking-wider text-[#5B5875]">Banking Metadata</span>
              <div className="grid grid-cols-2 gap-2">
                <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg">
                  <span className="text-[10px] text-slate-400 font-semibold block">Channel / Rail:</span>
                  <span className="font-bold text-slate-800">{selectedRow.channel || 'Direct / Card'}</span>
                </div>
                <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg">
                  <span className="text-[10px] text-slate-400 font-semibold block">Reference ID:</span>
                  <span className="font-mono font-bold text-slate-800 truncate block">{selectedRow.ref_no || 'None'}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-200">
            <button
              type="button"
              onClick={() => setSelectedRow(null)}
              className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition"
            >
              Close Audit Inspector
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
