import React, { useState } from 'react';
import { X, Play, Zap, FileText } from 'lucide-react';

const PRESETS = [
  {
    label: 'Urgent Double Charge ($199)',
    text: 'I was charged twice on my credit card for the annual subscription ($199). Please refund the duplicate transaction immediately as my account is overdrawn!',
  },
  {
    label: 'Checkout 500 Error Crash',
    text: 'When our users click the checkout button, the application crashes with a 500 Internal Server Error. All payment processing is down right now!',
  },
  {
    label: 'General Documentation Inquiry',
    text: 'Hello, could you point me to where I can find the documentation for webhook signatures and API rate limits?',
  },
  {
    label: 'Enterprise 200-Seat Deal (Sales)',
    text: 'Hi, I am VP of Engineering at Acme Corp (1,500 employees). We are evaluating your platform for 200 developers and need an enterprise demo this week.',
  },
];

const ExecutionModal = ({ isOpen, onClose, onExecute, isExecuting }) => {
  const [inputText, setInputText] = useState(PRESETS[0].text);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onExecute(inputText.trim());
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-xl rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400">
              <Zap className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">Execute Decision Flow</h2>
              <p className="text-xs text-slate-400">
                Inngest step-by-step evaluation with Gemini 2.5 Flash
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Presets */}
        <div className="mt-4">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Quick Scenario Presets
          </label>
          <div className="mt-2 flex flex-wrap gap-2">
            {PRESETS.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setInputText(p.text)}
                className="rounded-lg border border-slate-800 bg-slate-950/80 px-2.5 py-1 text-xs text-slate-300 hover:border-blue-500 hover:text-blue-400 transition"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Input Textarea */}
        <form onSubmit={handleSubmit} className="mt-4">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
            <FileText className="h-3.5 w-3.5 text-slate-400" />
            Input Message / Customer Ticket
          </label>
          <textarea
            rows={5}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type or paste customer inquiry or trigger payload..."
            className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-950 p-3 text-xs text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
            required
          />

          <div className="mt-6 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-xs font-medium text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isExecuting || !inputText.trim()}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2 text-xs font-semibold text-white shadow-lg shadow-blue-600/30 hover:bg-blue-500 transition disabled:opacity-50"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              {isExecuting ? 'Evaluating Flow...' : 'Start Execution'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ExecutionModal;
