import React, { useRef } from 'react';
import {
  Plus,
  Play,
  Download,
  Upload,
  Save,
  RotateCcw,
  Sparkles,
  Layers,
} from 'lucide-react';

const Toolbar = ({
  onAddDecisionNode,
  onAddActionNode,
  onOpenExecuteModal,
  onSaveFlow,
  onLoadTemplate,
  onExportJson,
  onImportJson,
  onResetFlow,
  isExecuting,
  currentTemplate,
}) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const json = JSON.parse(evt.target.result);
        onImportJson(json);
      } catch (err) {
        alert('Invalid JSON file format.');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  return (
    <header className="flex h-16 w-full items-center justify-between border-b border-slate-800/80 bg-slate-950/80 px-6 backdrop-blur-md">
      {/* Brand & Title */}
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 shadow-md shadow-blue-500/20">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
            AI Decision Flow Orchestrator
            <span className="rounded-full bg-blue-500/10 px-2 py-0.5 text-[10px] font-mono text-blue-400 border border-blue-500/20">
              React Flow + Inngest
            </span>
          </h1>
          <p className="text-[11px] text-slate-400">
            Autonomous branching workflows evaluated step-by-step with Gemini 3.1 Flash Lite
          </p>
        </div>
      </div>

      {/* Center Actions: Add Nodes & Templates */}
      <div className="flex items-center gap-2">
        {/* Template Selector */}
        <div className="relative flex items-center">
          <Layers className="absolute left-2.5 h-3.5 w-3.5 text-slate-400" />
          <select
            value={currentTemplate}
            onChange={(e) => onLoadTemplate(e.target.value)}
            className="h-9 rounded-lg border border-slate-800 bg-slate-900/90 pl-8 pr-3 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
          >
            <option value="support-triage">Template: Customer Support Triage</option>
            <option value="sales-qualifier">Template: Sales Lead Qualifier</option>
          </select>
        </div>

        <button
          onClick={onAddDecisionNode}
          className="flex h-9 items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900/90 px-3 text-xs font-medium text-slate-200 hover:border-slate-700 hover:bg-slate-800 transition"
        >
          <Plus className="h-3.5 w-3.5 text-blue-400" /> Decision Node
        </button>

        <button
          onClick={onAddActionNode}
          className="flex h-9 items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900/90 px-3 text-xs font-medium text-slate-200 hover:border-slate-700 hover:bg-slate-800 transition"
        >
          <Plus className="h-3.5 w-3.5 text-amber-400" /> Action Node
        </button>
      </div>

      {/* Right Controls: Save, Export, Import, Run */}
      <div className="flex items-center gap-2">
        <button
          onClick={onSaveFlow}
          title="Save to database"
          className="flex h-9 items-center gap-1 rounded-lg border border-slate-800 bg-slate-900/90 px-2.5 text-xs text-slate-300 hover:bg-slate-800 transition"
        >
          <Save className="h-3.5 w-3.5 text-slate-400" /> Save
        </button>

        <button
          onClick={onExportJson}
          title="Export JSON"
          className="flex h-9 items-center gap-1 rounded-lg border border-slate-800 bg-slate-900/90 px-2.5 text-xs text-slate-300 hover:bg-slate-800 transition"
        >
          <Download className="h-3.5 w-3.5 text-slate-400" /> Export
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileChange}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current && fileInputRef.current.click()}
          title="Import JSON"
          className="flex h-9 items-center gap-1 rounded-lg border border-slate-800 bg-slate-900/90 px-2.5 text-xs text-slate-300 hover:bg-slate-800 transition"
        >
          <Upload className="h-3.5 w-3.5 text-slate-400" /> Import
        </button>

        <button
          onClick={onResetFlow}
          title="Reset Graph"
          className="flex h-9 items-center gap-1 rounded-lg border border-slate-800 bg-slate-900/90 px-2.5 text-xs text-slate-300 hover:bg-slate-800 transition"
        >
          <RotateCcw className="h-3.5 w-3.5 text-slate-400" />
        </button>

        {/* Primary Run Button */}
        <button
          onClick={onOpenExecuteModal}
          disabled={isExecuting}
          className="flex h-9 items-center gap-2 rounded-lg bg-blue-600 px-4 text-xs font-semibold text-white shadow-lg shadow-blue-600/30 hover:bg-blue-500 transition disabled:opacity-50"
        >
          <Play className="h-3.5 w-3.5 fill-current" />
          {isExecuting ? 'Running Flow...' : 'Run Flow'}
        </button>
      </div>
    </header>
  );
};

export default Toolbar;
