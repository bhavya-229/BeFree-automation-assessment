import React, { useState } from 'react';
import type { StatementMetadata } from '../types';
import { getCurrencySymbol } from '../lib/currency';
import { Building2, Eye, EyeOff, Calendar, Hash, CreditCard, DollarSign } from 'lucide-react';

interface AccountDetailsCardProps {
  metadata?: StatementMetadata;
  defaultCurrency?: string;
}

export const AccountDetailsCard: React.FC<AccountDetailsCardProps> = ({
  metadata,
  defaultCurrency = 'AUD',
}) => {
  const [isMasked, setIsMasked] = useState(true);

  const bankName = metadata?.bank_name || 'Generic Bank Account';
  const rawAccNo = metadata?.account_number || '12345678';
  const sortCodeOrBsb = metadata?.sort_code_or_bsb || '062-000';
  const idType =
    metadata?.account_identifier_type ||
    (defaultCurrency === 'GBP' ? 'Sort Code' : defaultCurrency === 'INR' ? 'IFSC' : 'BSB');
  const currency = metadata?.currency || defaultCurrency;
  const currSymbol = getCurrencySymbol(currency);
  const period =
    metadata?.statement_period_start && metadata?.statement_period_end
      ? `${metadata.statement_period_start} — ${metadata.statement_period_end}`
      : metadata?.statement_period_end
      ? `As at ${metadata.statement_period_end}`
      : 'October 2023';

  const maskedAccNo = isMasked
    ? rawAccNo.length > 4
      ? `•••• •••• ${rawAccNo.slice(-4)}`
      : '•••• ••••'
    : rawAccNo;

  return (
    <div className="bg-white rounded-2xl border border-[#E4E2EC] p-6 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E4E2EC] gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-[#2E2C8F]">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-base text-[#1B1637]">{bankName}</h3>
            <p className="text-xs text-[#5B5875]">Account Holder & Statement Information</p>
          </div>
        </div>

        {/* Mask / Reveal Toggle */}
        <button
          type="button"
          onClick={() => setIsMasked(!isMasked)}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 bg-slate-50 hover:bg-slate-100 transition shadow-2xs self-start sm:self-auto"
        >
          {isMasked ? (
            <>
              <Eye className="w-3.5 h-3.5 text-slate-500" />
              <span>Reveal Account Details</span>
            </>
          ) : (
            <>
              <EyeOff className="w-3.5 h-3.5 text-slate-500" />
              <span>Mask Sensitive Data</span>
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-5">
        {/* Identifier (BSB or Sort Code) */}
        <div className="space-y-1">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875] flex items-center space-x-1">
            <CreditCard className="w-3 h-3 text-[#2E2C8F]" />
            <span>{idType}</span>
          </span>
          <p className="text-sm font-mono font-bold text-[#1B1637]">{sortCodeOrBsb}</p>
        </div>

        {/* Account Number */}
        <div className="space-y-1">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875] flex items-center space-x-1">
            <Hash className="w-3 h-3 text-[#2E2C8F]" />
            <span>Account Number</span>
          </span>
          <p className="text-sm font-mono font-bold text-[#1B1637]">{maskedAccNo}</p>
        </div>

        {/* Statement Period */}
        <div className="space-y-1">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875] flex items-center space-x-1">
            <Calendar className="w-3 h-3 text-[#2E2C8F]" />
            <span>Statement Period</span>
          </span>
          <p className="text-xs font-medium text-[#1B1637] truncate" title={period}>
            {period}
          </p>
        </div>

        {/* Base Currency */}
        <div className="space-y-1">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#5B5875] flex items-center space-x-1">
            <DollarSign className="w-3 h-3 text-[#2E2C8F]" />
            <span>Currency & Locality</span>
          </span>
          <div className="flex items-center space-x-1.5">
            <span className="px-2 py-0.5 rounded text-xs font-bold bg-indigo-50 text-[#2E2C8F] border border-indigo-100">
              {currency}
            </span>
            <span className="text-xs text-[#5B5875]">Day-first dates</span>
          </div>
        </div>
      </div>

      {(metadata?.opening_balance || metadata?.closing_balance) && (
        <div className="mt-4 pt-4 border-t border-dashed border-[#E4E2EC] flex flex-wrap items-center gap-6 text-xs">
          {metadata.opening_balance && (
            <div>
              <span className="text-[#5B5875]">Opening Balance: </span>
              <span className="font-bold tabular-nums text-slate-800">
                {currSymbol}{metadata.opening_balance}
              </span>
            </div>
          )}
          {metadata.closing_balance && (
            <div>
              <span className="text-[#5B5875]">Closing Balance: </span>
              <span className="font-bold tabular-nums text-slate-800">
                {currSymbol}{metadata.closing_balance}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
