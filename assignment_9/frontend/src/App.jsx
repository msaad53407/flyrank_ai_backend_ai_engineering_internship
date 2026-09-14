import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from '@xyflow/react';

import AIDecisionNode from './components/AIDecisionNode';
import ActionNode from './components/ActionNode';
import DecisionEdge from './components/DecisionEdge';
import Toolbar from './components/Toolbar';
import ExecutionModal from './components/ExecutionModal';
import ExecutionLogPanel from './components/ExecutionLogPanel';

// Default initial support triage graph
const INITIAL_NODES = [
  {
    id: 'node-1',
    type: 'decisionNode',
    position: { x: 320, y: 40 },
    data: {
      label: 'Billing Inquiry?',
      prompt: 'Is the user asking about billing, invoices, credit card charges, subscriptions, or payments?',
      nodeType: 'decision',
    },
  },
  {
    id: 'node-2',
    type: 'decisionNode',
    position: { x: 120, y: 260 },
    data: {
      label: 'Urgent / Double Charge?',
      prompt: 'Is the user reporting an urgent double charge, unauthorized transaction, or severe billing error?',
      nodeType: 'decision',
    },
  },
  {
    id: 'node-3',
    type: 'decisionNode',
    position: { x: 560, y: 260 },
    data: {
      label: 'Technical Bug?',
      prompt: 'Is the customer reporting a software bug, system crash, 500 error, or technical outage?',
      nodeType: 'decision',
    },
  },
  {
    id: 'action-urgent-billing',
    type: 'actionNode',
    position: { x: 20, y: 480 },
    data: {
      label: 'Priority Billing Escalation',
      action: 'Route immediately to Senior Financial Support & notify Slack #urgent-billing',
      nodeType: 'action',
    },
  },
  {
    id: 'action-std-billing',
    type: 'actionNode',
    position: { x: 250, y: 480 },
    data: {
      label: 'Standard Billing Queue',
      action: 'Assign ticket to Tier-1 Billing Specialist with standard 4-hour SLA',
      nodeType: 'action',
    },
  },
  {
    id: 'action-eng-bug',
    type: 'actionNode',
    position: { x: 470, y: 480 },
    data: {
      label: 'Engineering Bug Triage',
      action: 'File Jira issue in Backlog and attach system diagnostic logs',
      nodeType: 'action',
    },
  },
  {
    id: 'action-general-faq',
    type: 'actionNode',
    position: { x: 700, y: 480 },
    data: {
      label: 'Knowledge Base Reply',
      action: 'Send automated knowledge base self-serve link and general inquiry acknowledgement',
      nodeType: 'action',
    },
  },
];

const INITIAL_EDGES = [
  { id: 'e1-2', source: 'node-1', target: 'node-2', sourceHandle: 'yes', label: 'YES', type: 'decisionEdge' },
  { id: 'e1-3', source: 'node-1', target: 'node-3', sourceHandle: 'no', label: 'NO', type: 'decisionEdge' },
  { id: 'e2-urgent', source: 'node-2', target: 'action-urgent-billing', sourceHandle: 'yes', label: 'YES', type: 'decisionEdge' },
  { id: 'e2-std', source: 'node-2', target: 'action-std-billing', sourceHandle: 'no', label: 'NO', type: 'decisionEdge' },
  { id: 'e3-eng', source: 'node-3', target: 'action-eng-bug', sourceHandle: 'yes', label: 'YES', type: 'decisionEdge' },
  { id: 'e3-gen', source: 'node-3', target: 'action-general-faq', sourceHandle: 'no', label: 'NO', type: 'decisionEdge' },
];

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(INITIAL_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState(INITIAL_EDGES);

  const [currentTemplate, setCurrentTemplate] = useState('support-triage');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [isLogCollapsed, setIsLogCollapsed] = useState(false);

  // Register custom nodes and edges
  const nodeTypes = useMemo(
    () => ({
      decisionNode: AIDecisionNode,
      actionNode: ActionNode,
    }),
    []
  );

  const edgeTypes = useMemo(
    () => ({
      decisionEdge: DecisionEdge,
    }),
    []
  );

  // Node update callback
  const handleUpdateNode = useCallback((nodeId, newAttrs) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              ...newAttrs,
            },
          };
        }
        return node;
      })
    );
  }, [setNodes]);

  // Inject handleUpdateNode into data of all nodes
  useEffect(() => {
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: {
          ...n.data,
          onUpdateNode: handleUpdateNode,
        },
      }))
    );
  }, [handleUpdateNode, setNodes]);

  // Edge connection handler
  const onConnect = useCallback(
    (params) => {
      const isYes = (params.sourceHandle || '').toLowerCase().includes('yes');
      const label = isYes ? 'YES' : 'NO';
      const newEdge = {
        ...params,
        type: 'decisionEdge',
        label,
        data: { branch: label },
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  // Add Decision Node
  const handleAddDecisionNode = () => {
    const id = `node-${Date.now().toString().slice(-4)}`;
    const newNode = {
      id,
      type: 'decisionNode',
      position: { x: 300 + Math.random() * 50, y: 150 + Math.random() * 50 },
      data: {
        label: `Decision ${nodes.length + 1}`,
        prompt: 'Should this be approved?',
        nodeType: 'decision',
        onUpdateNode: handleUpdateNode,
      },
    };
    setNodes((nds) => nds.concat(newNode));
  };

  // Add Action Node
  const handleAddActionNode = () => {
    const id = `action-${Date.now().toString().slice(-4)}`;
    const newNode = {
      id,
      type: 'actionNode',
      position: { x: 300 + Math.random() * 50, y: 350 + Math.random() * 50 },
      data: {
        label: `Action ${nodes.length + 1}`,
        action: 'Execute automated workflow action',
        nodeType: 'action',
        onUpdateNode: handleUpdateNode,
      },
    };
    setNodes((nds) => nds.concat(newNode));
  };

  // Reset Graph
  const handleResetFlow = () => {
    setNodes(INITIAL_NODES);
    setEdges(INITIAL_EDGES);
    setExecutionResult(null);
  };

  // Load Template
  const handleLoadTemplate = async (templateId) => {
    setCurrentTemplate(templateId);
    try {
      const res = await fetch(`/api/templates/${templateId}`);
      if (res.ok) {
        const data = await res.json();
        const mappedNodes = data.nodes.map((n) => ({
          ...n,
          data: {
            ...n.data,
            onUpdateNode: handleUpdateNode,
          },
        }));
        const mappedEdges = data.edges.map((e) => ({
          ...e,
          type: 'decisionEdge',
        }));
        setNodes(mappedNodes);
        setEdges(mappedEdges);
        setExecutionResult(null);
      }
    } catch (e) {
      console.error('Failed to load template', e);
    }
  };

  // Save Flow to backend database
  const handleSaveFlow = async () => {
    try {
      const payload = {
        name: `${currentTemplate} Workflow`,
        nodes: nodes.map(({ id, type, position, data }) => ({
          id,
          type,
          position,
          data: { label: data.label, prompt: data.prompt, action: data.action, nodeType: data.nodeType },
        })),
        edges: edges.map(({ id, source, target, sourceHandle, label }) => ({
          id,
          source,
          target,
          sourceHandle,
          label,
        })),
      };

      const res = await fetch('/api/workflows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const saved = await res.json();
        alert(`Workflow successfully saved with ID: ${saved.id}`);
      }
    } catch (e) {
      alert('Error saving workflow.');
    }
  };

  // Export JSON
  const handleExportJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(
      JSON.stringify({ nodes, edges }, null, 2)
    );
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `ai-decision-flow-${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Import JSON
  const handleImportJson = (json) => {
    if (json.nodes && json.edges) {
      setNodes(
        json.nodes.map((n) => ({
          ...n,
          data: { ...n.data, onUpdateNode: handleUpdateNode },
        }))
      );
      setEdges(
        json.edges.map((e) => ({
          ...e,
          type: 'decisionEdge',
        }))
      );
      setExecutionResult(null);
    }
  };

  // Execute Workflow with Inngest & Gemini
  const handleExecute = async (inputContext) => {
    setIsExecuting(true);
    setExecutionResult(null);

    // Reset previous execution highlights
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: {
          ...n.data,
          executionResult: null,
          isTraversed: false,
          isSkipped: false,
          isRunning: true, // show thinking
        },
      }))
    );

    setEdges((eds) =>
      eds.map((e) => ({
        ...e,
        data: { ...e.data, isActive: false },
      }))
    );

    try {
      const payload = {
        workflow: {
          nodes: nodes.map(({ id, type, position, data }) => ({
            id,
            type,
            position,
            data: { label: data.label, prompt: data.prompt, action: data.action, nodeType: data.nodeType },
          })),
          edges: edges.map(({ id, source, target, sourceHandle, label }) => ({
            id,
            source,
            target,
            sourceHandle,
            label,
          })),
        },
        input_context: inputContext,
      };

      const res = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`HTTP error ${res.status}`);
      }

      const result = await res.json();
      setExecutionResult(result);
      setIsModalOpen(false);

      const pathSet = new Set(result.path_taken || []);
      const activeEdgesSet = new Set(result.active_edges || []);

      // Update nodes visual state
      setNodes((nds) =>
        nds.map((n) => {
          const isTraversed = pathSet.has(n.id);
          return {
            ...n,
            data: {
              ...n.data,
              isRunning: false,
              isTraversed,
              isSkipped: !isTraversed,
              executionResult: result.node_results ? result.node_results[n.id] : null,
            },
          };
        })
      );

      // Update edges visual state
      setEdges((eds) =>
        eds.map((e) => ({
          ...e,
          data: {
            ...e.data,
            isActive: activeEdgesSet.has(e.id),
          },
        }))
      );
    } catch (err) {
      alert(`Execution failed: ${err.message}`);
      setNodes((nds) =>
        nds.map((n) => ({
          ...n,
          data: { ...n.data, isRunning: false },
        }))
      );
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="flex h-screen w-screen flex-col bg-[#090d16] text-slate-100">
      {/* Top Navigation Toolbar */}
      <Toolbar
        onAddDecisionNode={handleAddDecisionNode}
        onAddActionNode={handleAddActionNode}
        onOpenExecuteModal={() => setIsModalOpen(true)}
        onSaveFlow={handleSaveFlow}
        onLoadTemplate={handleLoadTemplate}
        onExportJson={handleExportJson}
        onImportJson={handleImportJson}
        onResetFlow={handleResetFlow}
        isExecuting={isExecuting}
        currentTemplate={currentTemplate}
      />

      {/* Main Canvas Area */}
      <main className="relative flex-1 w-full h-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.2}
          maxZoom={1.5}
        >
          <Background color="#1e293b" gap={20} size={1} />
          <Controls className="!bg-slate-900 !border-slate-800 !fill-slate-300" />
          <MiniMap
            className="!bg-slate-950 !border-slate-800 rounded-xl overflow-hidden"
            nodeColor={(n) => (n.type === 'actionNode' ? '#f59e0b' : '#3b82f6')}
            maskColor="rgba(9, 13, 22, 0.7)"
          />
        </ReactFlow>

        {/* Real-time Execution Logs Panel */}
        <ExecutionLogPanel
          executionResult={executionResult}
          isCollapsed={isLogCollapsed}
          onToggleCollapse={() => setIsLogCollapsed((c) => !c)}
          onClear={() => setExecutionResult(null)}
        />
      </main>

      {/* Execution Input Modal */}
      <ExecutionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onExecute={handleExecute}
        isExecuting={isExecuting}
      />
    </div>
  );
}
