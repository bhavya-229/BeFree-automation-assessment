import React from 'react';
import type { NormalizedTransaction, ReconciliationSummary } from '../types';
import { PieChart } from 'lucide-react';

interface StatementInsightsProps {
  transactions: NormalizedTransaction[];
  recon: ReconciliationSummary;
  currency?: string;
}

export const StatementInsights: React.FC<StatementInsightsProps> = ({
  transactions,
  recon,
  currency = 'AUD',
}) => {
  const parseNum = (val: unknown): number => {
    if (typeof val === 'number') return isNaN(val) ? 0 : val;
    if (!val) return 0;
    const cleaned = String(val).replace(/,/g, '').trim();
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? 0 : parsed;
  };

  // Aggregate spending by category
  const categoryTotals: Record<string, { count: number; totalDebit: number; totalCredit: number }> = {};

  transactions.forEach((t) => {
    const cat = t.category || 'Other / Unclassified';
    if (!categoryTotals[cat]) {
      categoryTotals[cat] = { count: 0, totalDebit: 0, totalCredit: 0 };
    }
    categoryTotals[cat].count += 1;
    if (t.debit) {
      categoryTotals[cat].totalDebit += parseNum(t.debit);
    }
    if (t.credit) {
      categoryTotals[cat].totalCredit += parseNum(t.credit);
    }
  });

  const totalDebitOverall = parseNum(recon.total_debits) || 1;

  const sortedCategories = Object.entries(categoryTotals).sort(
    (a, b) => b[1].totalDebit - a[1].totalDebit
  );

  // Financial summary metrics
  const debits = transactions
    .filter((t) => t.debit)
    .map((t) => parseNum(t.debit));
  const maxDebit = debits.length > 0 ? Math.max(...debits) : 0;
  const avgDebit = debits.length > 0 ? debits.reduce((acc, v) => acc + v, 0) / debits.length : 0;
  const unclassifiedCount = transactions.filter(
    (t) => t.category === 'Other / Unclassified' || t.category_source === 'UNCLASSIFIED'
  ).length;

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-[#E4E2EC] p-5 shadow-2xs">
          <p className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875]">Largest Debit</p>
          <p className="text-2xl font-bold text-[#B42318] mt-1 tabular-nums">
            −{currency === 'GBP' ? '£' : '$'}{maxDebit.toFixed(2)}
          </p>
          <p className="text-xs text-[#5B5875] mt-1">Single highest outflow</p>
        </div>

        <div className="bg-white rounded-xl border border-[#E4E2EC] p-5 shadow-2xs">
          <p className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875]">Average Expense</p>
          <p className="text-2xl font-bold text-slate-900 mt-1 tabular-nums">
            {currency === 'GBP' ? '£' : '$'}{avgDebit.toFixed(2)}
          </p>
          <p className="text-xs text-[#5B5875] mt-1">Across {debits.length} debit transactions</p>
        </div>

        <div className="bg-white rounded-xl border border-[#E4E2EC] p-5 shadow-2xs">
          <p className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875]">Net Cash Flow</p>
          <p className={`text-2xl font-bold mt-1 tabular-nums ${
            parseFloat(recon.net_movement) >= 0 ? 'text-[#137A3F]' : 'text-[#B42318]'
          }`}>
            {parseFloat(recon.net_movement) >= 0 ? '+' : '−'}
            {currency === 'GBP' ? '£' : '$'}{Math.abs(parseFloat(recon.net_movement)).toFixed(2)}
          </p>
          <p className="text-xs text-[#5B5875] mt-1">Credits minus debits</p>
        </div>

        <div className="bg-white rounded-xl border border-[#E4E2EC] p-5 shadow-2xs">
          <p className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875]">Review Queue</p>
          <div className="flex items-center space-x-2 mt-1">
            {unclassifiedCount === 0 ? (
              <span className="text-2xl font-bold text-[#137A3F]">0</span>
            ) : (
              <span className="text-2xl font-bold text-amber-600">{unclassifiedCount}</span>
            )}
          </div>
          <p className="text-xs text-[#5B5875] mt-1">
            {unclassifiedCount === 0 ? '100% classified' : 'Pending review'}
          </p>
        </div>
      </div>

      {/* Category Breakdown Surface */}
      <div className="bg-white rounded-2xl border border-[#E4E2EC] p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#E4E2EC]">
          <div className="flex items-center space-x-2">
            <PieChart className="w-5 h-5 text-[#2E2C8F]" />
            <h3 className="font-extrabold text-base text-[#1B1637]">
              Expense Distribution by Category
            </h3>
          </div>
          <span className="text-xs text-[#5B5875]">
            {sortedCategories.length} Active Categories
          </span>
        </div>

        <div className="space-y-4 pt-2">
          {sortedCategories.map(([cat, stat]) => {
            const sharePercent = totalDebitOverall > 0
              ? Math.min(100, Math.round((stat.totalDebit / totalDebitOverall) * 100))
              : 0;

            return (
              <div key={cat} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-[#1B1637] flex items-center space-x-1.5">
                    <span>{cat}</span>
                    <span className="text-[11px] font-normal text-[#5B5875]">
                      ({stat.count} {stat.count === 1 ? 'txn' : 'txns'})
                    </span>
                  </span>
                  <div className="flex items-center space-x-3 tabular-nums font-semibold">
                    {stat.totalDebit > 0 && (
                      <span className="text-[#B42318]">
                        −{currency === 'GBP' ? '£' : '$'}{stat.totalDebit.toFixed(2)}
                      </span>
                    )}
                    {stat.totalCredit > 0 && (
                      <span className="text-[#137A3F]">
                        +{currency === 'GBP' ? '£' : '$'}{stat.totalCredit.toFixed(2)}
                      </span>
                    )}
                    <span className="text-slate-400 font-mono w-10 text-right">
                      {sharePercent}%
                    </span>
                  </div>
                </div>

                <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-[#2E2C8F] transition-all duration-300"
                    style={{ width: `${Math.max(sharePercent, 2)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
