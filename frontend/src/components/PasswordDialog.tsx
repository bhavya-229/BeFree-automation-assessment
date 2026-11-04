import React, { useState } from 'react';
import { Lock, Eye, EyeOff, AlertCircle, Loader2, X } from 'lucide-react';

interface PasswordDialogProps {
  filename: string;
  isOpen: boolean;
  isLoading: boolean;
  errorMessage: string | null;
  onSubmit: (password: string) => void;
  onCancel: () => void;
}

export const PasswordDialog: React.FC<PasswordDialogProps> = ({
  filename,
  isOpen,
  isLoading,
  errorMessage,
  onSubmit,
  onCancel,
}) => {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!password.trim()) return;
    onSubmit(password);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-5 animate-in zoom-in-95 duration-150">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-base text-[#1B1637]">Password Required</h3>
              <p className="text-xs text-[#5B5875] truncate max-w-xs">{filename}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onCancel}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-[#5B5875] leading-relaxed">
          This bank statement is encrypted with a password. Financial institutions typically protect statements using your <strong>Date of Birth (e.g., DDMMYYYY)</strong>, <strong>PAN</strong>, or the <strong>last 4 digits of your account</strong>.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold uppercase tracking-wider text-[#1B1637] block">
              Enter Statement Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                autoFocus
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full text-xs font-mono px-3 py-2.5 pr-10 border border-slate-300 rounded-xl focus:ring-2 focus:ring-[#2E2C8F] focus:outline-hidden"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {errorMessage && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-800 text-xs flex items-center space-x-2 animate-in shake">
              <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-2">
            <button
              type="button"
              disabled={isLoading}
              onClick={onCancel}
              className="px-4 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !password.trim()}
              className="inline-flex items-center space-x-1.5 px-4 py-2 bg-[#2E2C8F] hover:bg-[#25237A] text-white rounded-xl text-xs font-bold shadow-xs transition disabled:opacity-50"
            >
              {isLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              <span>{isLoading ? 'Decrypting...' : 'Unlock & Process'}</span>
            </button>
          </div>
        </form>

        <p className="text-[10px] text-center text-slate-400">
          🔒 Zero-Storage Guarantee: Passwords live only in memory during decryption and are never logged or saved to disk.
        </p>
      </div>
    </div>
  );
};
