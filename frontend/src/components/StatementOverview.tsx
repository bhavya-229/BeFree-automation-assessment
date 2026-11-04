import React, { useState } from 'react';
import type { StatementRecord } from '../types';
import { getExportCsvUrl, getExportXlsxUrl } from '../lib/api';
import { getCurrencySymbol } from '../lib/currency';
import { Download, FileText, CheckCircle2, AlertTriangle, Layers, ListOrdered, BarChart3, Calculator } from 'lucide-react';
import { AccountDetailsCard } from './AccountDetailsCard';
import { TransactionTable } from './TransactionTable';
import { StatementInsights } from './StatementInsights';
import { StatementValidation } from './StatementValidation';

interface StatementOverviewProps {
  record: StatementRecord;
}

export const StatementOverview: React.FC<StatementOverviewProps> = ({ record }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'transactions' | 'insights' | 'validation'>('overview');

  const { reconciliation_summary: recon, doc_type_report: docType, metadata } = record;
  const currency = metadata?.currency || 'AUD';
  const currSymbol = getCurrencySymbol(currency);

  const isReconciled = recon.quality_score >= 90.0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* File & Export Header Bar */}
      <div className="bg-white rounded-2xl border border-[#E4E2EC] p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xs">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-[#2E2C8F] shadow-2xs">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xl font-extrabold text-[#1B1637]">{record.filename}</h2>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                docType.doc_type === 'DIGITAL'
                  ? 'bg-emerald-50 text-[#137A3F] border border-emerald-200'
                  : docType.doc_type === 'SCANNED'
                  ? 'bg-amber-50 text-amber-800 border border-amber-200'
                  : 'bg-purple-50 text-purple-700 border border-purple-200'
              }`}>
                {docType.doc_type} PDF ({record.page_count} {record.page_count === 1 ? 'Page' : 'Pages'})
              </span>
            </div>
            <div className="flex items-center space-x-3 text-xs text-[#5B5875] mt-1 font-mono">
              <span className="truncate max-w-xs" title={record.sha256}>
                SHA-256: {record.sha256.slice(0, 16)}...
              </span>
              <span>•</span>
              <span className="font-sans font-medium">{docType.reason}</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <a
            href={getExportCsvUrl(record.id)}
            download
            className="flex-1 md:flex-none inline-flex items-center justify-center space-x-2 px-4 py-2.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-bold shadow-2xs transition"
          >
            <Download className="w-4 h-4 text-slate-500" />
            <span>Export CSV</span>
          </a>
          <a
            href={getExportXlsxUrl(record.id)}
            download
            className="flex-1 md:flex-none inline-flex items-center justify-center space-x-2 px-4 py-2.5 bg-[#2E2C8F] hover:bg-[#25237A] text-white rounded-xl text-xs font-bold shadow-sm transition"
          >
            <Download className="w-4 h-4 text-white" />
            <span>Export Excel (.xlsx)</span>
          </a>
        </div>
      </div>

      {/* Workspace Tabs Navigation (Prompt Section 3.2) */}
      <div className="border-b border-[#E4E2EC] flex items-center space-x-2 sm:space-x-8">
        <button
          type="button"
          onClick={() => setActiveTab('overview')}
          className={`pb-3 text-xs sm:text-sm font-bold flex items-center space-x-2 border-b-2 transition ${
            activeTab === 'overview'
              ? 'border-[#2E2C8F] text-[#2E2C8F]'
              : 'border-transparent text-[#5B5875] hover:text-[#1B1637]'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Overview</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('transactions')}
          className={`pb-3 text-xs sm:text-sm font-bold flex items-center space-x-2 border-b-2 transition ${
            activeTab === 'transactions'
              ? 'border-[#2E2C8F] text-[#2E2C8F]'
              : 'border-transparent text-[#5B5875] hover:text-[#1B1637]'
          }`}
        >
          <ListOrdered className="w-4 h-4" />
          <span>Transactions</span>
          <span className="bg-slate-100 text-slate-600 px-1.5 py-0.2 rounded-full text-[10px] font-mono">
            {record.transactions.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('insights')}
          className={`pb-3 text-xs sm:text-sm font-bold flex items-center space-x-2 border-b-2 transition ${
            activeTab === 'insights'
              ? 'border-[#2E2C8F] text-[#2E2C8F]'
              : 'border-transparent text-[#5B5875] hover:text-[#1B1637]'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Insights</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('validation')}
          className={`pb-3 text-xs sm:text-sm font-bold flex items-center space-x-2 border-b-2 transition ${
            activeTab === 'validation'
              ? 'border-[#2E2C8F] text-[#2E2C8F]'
              : 'border-transparent text-[#5B5875] hover:text-[#1B1637]'
          }`}
        >
          <Calculator className="w-4 h-4" />
          <span>Validation & Proof</span>
          <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
            isReconciled ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
          }`}>
            {recon.quality_score}%
          </span>
        </button>
      </div>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Account Details Card */}
          <AccountDetailsCard metadata={metadata} defaultCurrency={currency} />

          {/* 4 Financial KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-2xl border border-[#E4E2EC] p-5 shadow-2xs">
              <p className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875]">Transactions</p>
              <p className="text-2xl font-extrabold text-[#1B1637] mt-1 tabular-nums">{recon.total_transactions}</p>
              <p className="text-xs text-[#5B5875] mt-1">{record.page_count} {record.page_count === 1 ? 'page' : 'pages'} extracted</p>
            </div>

            <div className="bg-white rounded-2xl border border-[#E4E2EC] p-5 shadow-2xs">
              <p className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875]">Total Debits (Dr)</p>
              <p className="text-2xl font-extrabold text-[#B42318] mt-1 tabular-nums">
                −{currSymbol}{recon.total_debits}
              </p>
              <p className="text-xs text-[#5B5875] mt-1">Expenses & withdrawals</p>
            </div>

            <div className="bg-white rounded-2xl border border-[#E4E2EC] p-5 shadow-2xs">
              <p className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875]">Total Credits (Cr)</p>
              <p className="text-2xl font-extrabold text-[#137A3F] mt-1 tabular-nums">
                +{currSymbol}{recon.total_credits}
              </p>
              <p className="text-xs text-[#5B5875] mt-1">Income & deposits</p>
            </div>

            <div className="bg-white rounded-2xl border border-[#E4E2EC] p-5 shadow-2xs">
              <p className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875]">Quality Score</p>
              <div className="flex items-center space-x-2 mt-1">
                {isReconciled ? (
                  <CheckCircle2 className="w-6 h-6 text-[#137A3F]" />
                ) : (
                  <AlertTriangle className="w-6 h-6 text-amber-500" />
                )}
                <span className="text-2xl font-extrabold text-[#1B1637] tabular-nums">{recon.quality_score}%</span>
              </div>
              <p className="text-xs text-[#5B5875] mt-1 truncate" title={recon.discrepancy_explanation}>
                {recon.discrepancy_explanation}
              </p>
            </div>
          </div>

          {/* Document Inspection Diagnostics */}
          <div className="bg-white rounded-2xl border border-[#E4E2EC] p-6 shadow-xs space-y-4">
            <h4 className="font-extrabold text-sm text-[#1B1637]">Document Page Diagnostics</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                <span className="font-semibold text-slate-500 block">Digital Text Pages:</span>
                <span className="font-bold text-slate-800 text-sm">{docType.digital_page_count} of {docType.total_pages}</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                <span className="font-semibold text-slate-500 block">Scanned / OCR Pages:</span>
                <span className="font-bold text-slate-800 text-sm">{docType.scanned_page_count} of {docType.total_pages}</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                <span className="font-semibold text-slate-500 block">Classification Privacy:</span>
                <span className="font-bold text-emerald-700 text-sm">100% Non-LLM (Local)</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Transactions Grid */}
      {activeTab === 'transactions' && (
        <TransactionTable
          statementId={record.id}
          initialTransactions={record.transactions}
          currency={currency}
        />
      )}

      {/* Tab 3: Insights */}
      {activeTab === 'insights' && (
        <StatementInsights
          transactions={record.transactions}
          recon={recon}
          currency={currency}
        />
      )}

      {/* Tab 4: Validation */}
      {activeTab === 'validation' && (
        <StatementValidation
          transactions={record.transactions}
          recon={recon}
          currency={currency}
        />
      )}
    </div>
  );
};
