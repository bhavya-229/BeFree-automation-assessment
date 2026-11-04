import React, { useState } from 'react';
import { Header } from './components/Header';
import { FileUpload } from './components/FileUpload';
import { StatementOverview } from './components/StatementOverview';
import type { StatementRecord } from './types';
import { ArrowLeft } from 'lucide-react';

export const App: React.FC = () => {
  const [statement, setStatement] = useState<StatementRecord | null>(null);
  const [activeView, setActiveView] = useState<'workspace' | 'rules' | 'help'>('workspace');

  return (
    <div className="min-h-screen bg-[#F8F9FC] flex flex-col font-sans text-[#1B1637]">
      <Header
        activeView={activeView}
        onViewChange={(view) => setActiveView(view)}
        onSelectStatement={(rec) => setStatement(rec)}
        activeStatementId={statement?.id}
      />

      <main className="flex-1 pb-16">
        {!statement ? (
          <div className="py-6">
            <FileUpload onUploadSuccess={(rec) => setStatement(rec)} />
          </div>
        ) : (
          <div>
            {/* Top Back Toolbar */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4 flex justify-between items-center">
              <button
                type="button"
                onClick={() => setStatement(null)}
                className="inline-flex items-center space-x-1.5 text-xs font-bold text-[#5B5875] hover:text-[#1B1637] bg-white border border-[#E4E2EC] px-3.5 py-1.5 rounded-xl shadow-2xs hover:bg-slate-50 transition"
              >
                <ArrowLeft className="w-3.5 h-3.5 text-[#2E2C8F]" />
                <span>Upload Another Statement</span>
              </button>
            </div>

            {/* Statement Workspace with 4 deep tabs */}
            <StatementOverview record={statement} />
          </div>
        )}
      </main>

      {/* Signature Fintech Footer with 4px Gradient Bar */}
      <footer className="mt-auto bg-white border-t border-[#E4E2EC]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row items-center justify-between text-xs text-[#5B5875] gap-2">
          <p>© 2026 Bank Statement Processor • Befree AI & Automation Assessment</p>
          <div className="flex items-center space-x-4">
            <span className="font-semibold text-emerald-700">Strict Non-LLM Architecture</span>
            <span>•</span>
            <span>Zero Data Exfiltration</span>
          </div>
        </div>
        <div className="h-1 w-full bg-gradient-to-r from-[#F9A03F] via-[#F0568A] via-[#4040D6] to-[#24124F]" />
      </footer>
    </div>
  );
};

export default App;
