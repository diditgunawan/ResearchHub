import React, { useState } from 'react';
import { Project } from '../api/client';
import { GitFork, AlertCircle, Search, Compass, ShieldAlert } from 'lucide-react';

interface LineageNode {
  work_id: string;
  title: string;
  year?: number;
  doi?: string;
  family_id?: string;
  family_label?: string;
  role: 'root' | 'placed' | 'needs_review' | 'unplaced';
  parent_work_id?: string;
  parent_title?: string;
  confidence?: number;
  confidence_band?: 'high' | 'medium' | 'low';
  evidence: {
    cit?: number;
    sem?: number;
    kw?: number;
    chr?: number;
    shared_concepts?: string[];
  };
  missing_flags: string[];
  user_override?: {
    by: string;
    at: string;
    reason?: string;
  };
}

interface MapCluster {
  id: string;
  label: string;
  keywords: string[];
  size: number;
  is_other: boolean;
}

interface LineageGraph {
  run_id: string;
  project_id: string;
  record_count: number;
  families: MapCluster[];
  nodes: LineageNode[];
  edges: {
    parent_work_id: string;
    child_work_id: string;
    score: number;
    evidence: Record<string, any>;
  }[];
  roots: string[];
  status: string;
}

interface PositioningResult {
  id: string;
  closest_family_label?: string;
  runner_up_family_label?: string;
  top_parents: {
    work_id: string;
    title: string;
    year?: number;
    score: number;
    component_scores: { cit: number; sem: number; kw: number; chr: number };
    shared_concepts: string[];
  }[];
  shared_concepts: string[];
  distinctive_concepts: string[];
  fit_label: string;
  disclaimer: string;
}

interface GapSignal {
  id: string;
  kind: string;
  work_title?: string;
  excerpt?: string;
  frequency: number;
  confidence?: number;
  disclaimer: string;
}

export const LineagePage: React.FC<{ activeProject: Project | null }> = ({ activeProject }) => {
  const [loading, setLoading] = useState(false);
  const [graph, setGraph] = useState<LineageGraph | null>(null);
  const [viewMode, setViewMode] = useState<'tree' | 'audit' | 'positioning' | 'gaps'>('tree');
  const [selectedNode, setSelectedNode] = useState<LineageNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [overrideModal, setOverrideModal] = useState<{ open: boolean; node: LineageNode | null }>({
    open: false,
    node: null,
  });
  const [newParentId, setNewParentId] = useState('');

  // Positioning state
  const [msTitle, setMsTitle] = useState('');
  const [msAbstract, setMsAbstract] = useState('');
  const [positioningResult, setPositioningResult] = useState<PositioningResult | null>(null);
  const [positioningLoading, setPositioningLoading] = useState(false);

  // Gap signals state
  const [gaps, setGaps] = useState<GapSignal[]>([]);

  const handleRunLineage = async () => {
    if (!activeProject) return;
    setLoading(true);
    try {
      const res = await fetch(`/projects/${activeProject.id}/lineage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('rf_session_token') || ''}`,
        },
        body: JSON.stringify({ kind: 'lineage', scope_type: 'library_all', seed: 42 }),
      });
      if (res.ok) {
        const data = await res.json();
        setGraph(data);
        if (data.nodes.length > 0) {
          setSelectedNode(data.nodes[0]);
        }
        // Also fetch gaps
        const gapsRes = await fetch(`/projects/${activeProject.id}/gaps/${data.run_id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('rf_session_token') || ''}`,
          },
        });
        if (gapsRes.ok) {
          setGaps(await gapsRes.json());
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyOverride = async () => {
    if (!activeProject || !graph || !overrideModal.node) return;
    try {
      const res = await fetch(`/projects/${activeProject.id}/lineage/${graph.run_id}/override`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('rf_session_token') || ''}`,
        },
        body: JSON.stringify({
          work_id: overrideModal.node.work_id,
          parent_work_id: newParentId || null,
          reason: 'Manual expert correction',
        }),
      });
      if (res.ok) {
        const updatedNode = await res.json();
        setGraph({
          ...graph,
          nodes: graph.nodes.map((n) => (n.work_id === updatedNode.work_id ? updatedNode : n)),
        });
        setSelectedNode(updatedNode);
        setOverrideModal({ open: false, node: null });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunPositioning = async () => {
    if (!activeProject || !graph || !msTitle || !msAbstract) return;
    setPositioningLoading(true);
    try {
      const res = await fetch(`/projects/${activeProject.id}/positioning`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('rf_session_token') || ''}`,
        },
        body: JSON.stringify({
          lineage_run_id: graph.run_id,
          title: msTitle,
          abstract: msAbstract,
          retain_text: false,
        }),
      });
      if (res.ok) {
        setPositioningResult(await res.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setPositioningLoading(false);
    }
  };

  if (!activeProject) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 text-center text-[#4A5B68]">
        Select or create a project to view literature lineage.
      </div>
    );
  }

  const filteredNodes = (graph?.nodes || []).filter(
    (n) =>
      n.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (n.family_label && n.family_label.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Top Banner / Actions */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-[#D7DEE3] mb-6">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-serif font-bold text-[#12202B]">Genealogical Lineage & Topic Map</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#E3F0F5] text-[#0B4A63]">
              MAP-001..019 Compliant
            </span>
          </div>
          <p className="text-sm text-[#4A5B68] mt-1">
            Deterministic parent-child lineage DAG enforcing Year(p) ≤ Year(c) and 4-component evidence weights.
          </p>
        </div>

        <div className="mt-4 md:mt-0 flex items-center space-x-3">
          <button
            onClick={handleRunLineage}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-[#0B5C7A] text-white rounded-md text-sm font-medium hover:bg-[#08455C] transition-colors disabled:opacity-50"
          >
            <GitFork className="w-4 h-4" />
            <span>{loading ? 'Computing DAG...' : graph ? 'Recompute Lineage' : 'Compute Lineage DAG'}</span>
          </button>
        </div>
      </div>

      {graph ? (
        <div>
          {/* Metrics summary bar */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white p-3.5 rounded-lg border border-[#D7DEE3]">
              <div className="text-xs text-[#4A5B68]">Total Works Analyzed</div>
              <div className="text-xl font-bold text-[#12202B]">{graph.record_count}</div>
            </div>
            <div className="bg-white p-3.5 rounded-lg border border-[#D7DEE3]">
              <div className="text-xs text-[#4A5B68]">Research Families</div>
              <div className="text-xl font-bold text-[#0B5C7A]">{graph.families.length}</div>
            </div>
            <div className="bg-white p-3.5 rounded-lg border border-[#D7DEE3]">
              <div className="text-xs text-[#4A5B68]">Foundational Roots</div>
              <div className="text-xl font-bold text-[#1F5429]">{graph.roots.length}</div>
            </div>
            <div className="bg-white p-3.5 rounded-lg border border-[#D7DEE3]">
              <div className="text-xs text-[#4A5B68]">High Confidence Links</div>
              <div className="text-xl font-bold text-[#1F5429]">
                {graph.nodes.filter((n) => n.confidence_band === 'high').length}
              </div>
            </div>
            <div className="bg-white p-3.5 rounded-lg border border-[#D7DEE3]">
              <div className="text-xs text-[#4A5B68]">Needs Review</div>
              <div className="text-xl font-bold text-[#8A5200]">
                {graph.nodes.filter((n) => n.role === 'needs_review').length}
              </div>
            </div>
          </div>

          {/* Navigation Sub-Tabs */}
          <div className="flex border-b border-[#D7DEE3] mb-6 space-x-8">
            <button
              onClick={() => setViewMode('tree')}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                viewMode === 'tree' ? 'border-[#0B5C7A] text-[#0B5C7A]' : 'border-transparent text-[#4A5B68]'
              }`}
            >
              Genealogical Tree View
            </button>
            <button
              onClick={() => setViewMode('audit')}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                viewMode === 'audit' ? 'border-[#0B5C7A] text-[#0B5C7A]' : 'border-transparent text-[#4A5B68]'
              }`}
            >
              Audit Table & Overrides
            </button>
            <button
              onClick={() => setViewMode('positioning')}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                viewMode === 'positioning' ? 'border-[#0B5C7A] text-[#0B5C7A]' : 'border-transparent text-[#4A5B68]'
              }`}
            >
              Manuscript Positioning
            </button>
            <button
              onClick={() => setViewMode('gaps')}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                viewMode === 'gaps' ? 'border-[#0B5C7A] text-[#0B5C7A]' : 'border-transparent text-[#4A5B68]'
              }`}
            >
              Research Gap Signals ({gaps.length})
            </button>
          </div>

          {/* VIEW: TREE */}
          {viewMode === 'tree' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left 2 Cols: Tree / DAG Node List */}
              <div className="lg:col-span-2 bg-white rounded-lg border border-[#D7DEE3] p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-serif font-bold text-[#12202B]">Historical Precedence Branches</h3>
                  <div className="text-xs text-[#4A5B68]">Strict Chronological Direction (Roots → Leaves)</div>
                </div>

                <div className="space-y-4">
                  {graph.families.map((family) => {
                    const familyNodes = graph.nodes.filter((n) => n.family_id === family.id);
                    return (
                      <div key={family.id} className="border border-[#D7DEE3] rounded-lg p-4 bg-[#FBFDFD]">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <span className="font-serif font-bold text-sm text-[#0B5C7A]">{family.label}</span>
                            <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-700">
                              {familyNodes.length} papers
                            </span>
                          </div>
                          <div className="flex space-x-1">
                            {family.keywords.map((kw, idx) => (
                              <span key={idx} className="text-xs px-1.5 py-0.5 rounded bg-[#E3F0F5] text-[#0B4A63]">
                                {kw}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Nodes in this family */}
                        <div className="space-y-2">
                          {familyNodes.map((node) => (
                            <div
                              key={node.work_id}
                              onClick={() => setSelectedNode(node)}
                              className={`p-3 rounded-md border cursor-pointer transition-all ${
                                selectedNode?.work_id === node.work_id
                                  ? 'border-[#0B5C7A] bg-[#F2F8FA]'
                                  : 'border-[#E2E8F0] bg-white hover:border-[#0B5C7A]'
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <div>
                                  <div className="flex items-center space-x-2">
                                    <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-[#12202B] text-white">
                                      {node.year || 'Unknown'}
                                    </span>
                                    <span className="text-sm font-semibold text-[#12202B] line-clamp-1">
                                      {node.title}
                                    </span>
                                  </div>
                                  {node.parent_title && (
                                    <div className="text-xs text-[#4A5B68] mt-1 pl-2 border-l-2 border-[#0B5C7A]">
                                      ↳ Descendant of: <span className="italic">{node.parent_title}</span>
                                    </div>
                                  )}
                                </div>
                                <div className="flex items-center space-x-2">
                                  {node.role === 'root' ? (
                                    <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-[#E5F3E8] text-[#1F5429]">
                                      ROOT
                                    </span>
                                  ) : node.confidence_band === 'high' ? (
                                    <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-[#E5F3E8] text-[#1F5429]">
                                      HIGH
                                    </span>
                                  ) : node.confidence_band === 'medium' ? (
                                    <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-[#FFF5E5] text-[#8A5200]">
                                      MEDIUM
                                    </span>
                                  ) : (
                                    <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-[#FBE4E4] text-[#8A1C1C]">
                                      NEEDS REVIEW
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Right Col: Evidence Breakdown Drawer */}
              <div className="bg-white rounded-lg border border-[#D7DEE3] p-5 h-fit sticky top-24">
                {selectedNode ? (
                  <div>
                    <div className="flex items-center justify-between pb-3 border-b border-[#D7DEE3]">
                      <h4 className="font-serif font-bold text-base text-[#12202B]">Evidence Audit</h4>
                      <button
                        onClick={() => setOverrideModal({ open: true, node: selectedNode })}
                        className="text-xs text-[#0B5C7A] hover:underline font-medium"
                      >
                        Manual Override
                      </button>
                    </div>

                    <div className="mt-4 space-y-4">
                      <div>
                        <div className="text-xs text-[#4A5B68]">Title</div>
                        <div className="text-sm font-semibold text-[#12202B]">{selectedNode.title}</div>
                      </div>

                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div>
                          <span className="text-[#4A5B68]">Publication Year:</span>{' '}
                          <span className="font-semibold">{selectedNode.year || 'Missing'}</span>
                        </div>
                        <div>
                          <span className="text-[#4A5B68]">DOI:</span>{' '}
                          <span className="font-mono text-xs">{selectedNode.doi || 'None'}</span>
                        </div>
                        <div>
                          <span className="text-[#4A5B68]">Family Branch:</span>{' '}
                          <span className="font-semibold">{selectedNode.family_label}</span>
                        </div>
                        <div>
                          <span className="text-[#4A5B68]">Assigned Role:</span>{' '}
                          <span className="font-semibold uppercase">{selectedNode.role}</span>
                        </div>
                      </div>

                      {/* 4-Component Evidence Radar / Progress */}
                      <div className="p-3 bg-[#F6F8F9] rounded-lg border border-[#D7DEE3]">
                        <div className="text-xs font-bold text-[#12202B] mb-2">
                          Component Breakdown (Score: {Math.round((selectedNode.confidence || 0) * 100)}%)
                        </div>

                        <div className="space-y-2 text-xs">
                          <div>
                            <div className="flex justify-between text-[#4A5B68]">
                              <span>Direct Citation (35%)</span>
                              <span className="font-semibold">
                                {Math.round((selectedNode.evidence?.cit || 0) * 100)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden mt-0.5">
                              <div
                                className="bg-[#0B5C7A] h-full"
                                style={{ width: `${(selectedNode.evidence?.cit || 0) * 100}%` }}
                              />
                            </div>
                          </div>

                          <div>
                            <div className="flex justify-between text-[#4A5B68]">
                              <span>Semantic Cosine (35%)</span>
                              <span className="font-semibold">
                                {Math.round((selectedNode.evidence?.sem || 0) * 100)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden mt-0.5">
                              <div
                                className="bg-[#0B5C7A] h-full"
                                style={{ width: `${(selectedNode.evidence?.sem || 0) * 100}%` }}
                              />
                            </div>
                          </div>

                          <div>
                            <div className="flex justify-between text-[#4A5B68]">
                              <span>Keyword Jaccard (20%)</span>
                              <span className="font-semibold">
                                {Math.round((selectedNode.evidence?.kw || 0) * 100)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden mt-0.5">
                              <div
                                className="bg-[#0B5C7A] h-full"
                                style={{ width: `${(selectedNode.evidence?.kw || 0) * 100}%` }}
                              />
                            </div>
                          </div>

                          <div>
                            <div className="flex justify-between text-[#4A5B68]">
                              <span>Chronology Decay (10%)</span>
                              <span className="font-semibold">
                                {Math.round((selectedNode.evidence?.chr || 0) * 100)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden mt-0.5">
                              <div
                                className="bg-[#0B5C7A] h-full"
                                style={{ width: `${(selectedNode.evidence?.chr || 0) * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Missing Metadata Flags */}
                      {selectedNode.missing_flags.length > 0 && (
                        <div className="p-3 bg-[#FFF5E5] rounded-md border border-[#FAD899] text-xs">
                          <div className="flex items-center space-x-1.5 font-bold text-[#8A5200] mb-1">
                            <AlertCircle className="w-3.5 h-3.5" />
                            <span>Missing Metadata Flags</span>
                          </div>
                          <ul className="list-disc pl-4 space-y-0.5 text-[#8A5200]">
                            {selectedNode.missing_flags.map((f, i) => (
                              <li key={i}>{f}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* User override indicator */}
                      {selectedNode.user_override && (
                        <div className="p-2.5 bg-[#E3F0F5] rounded text-xs text-[#0B4A63] border border-[#B3D6E5]">
                          <span className="font-bold">Manually Overridden:</span> {selectedNode.user_override.reason} (
                          {selectedNode.user_override.at.slice(0, 10)})
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-[#4A5B68] text-sm">Select a paper to inspect evidence</div>
                )}
              </div>
            </div>
          )}

          {/* VIEW: AUDIT TABLE */}
          {viewMode === 'audit' && (
            <div className="bg-white rounded-lg border border-[#D7DEE3] overflow-hidden">
              <div className="p-4 border-b border-[#D7DEE3] flex justify-between items-center">
                <div className="flex items-center space-x-3 w-1/3">
                  <Search className="w-4 h-4 text-[#4A5B68]" />
                  <input
                    type="text"
                    placeholder="Search by title or branch..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full text-sm border border-[#D7DEE3] rounded-md px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-[#0B5C7A]"
                  />
                </div>
                <div className="text-xs text-[#4A5B68]">
                  Showing {filteredNodes.length} of {graph.record_count} records
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-[#F6F8F9] border-b border-[#D7DEE3] text-xs text-[#4A5B68] uppercase">
                    <tr>
                      <th className="py-3 px-4">Title & Year</th>
                      <th className="py-3 px-4">Branch Family</th>
                      <th className="py-3 px-4">Parent Paper</th>
                      <th className="py-3 px-4">Confidence</th>
                      <th className="py-3 px-4">Evidence (Cit/Sem/Kw/Chr)</th>
                      <th className="py-3 px-4">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#D7DEE3]">
                    {filteredNodes.map((n) => (
                      <tr key={n.work_id} className="hover:bg-gray-50">
                        <td className="py-3 px-4 max-w-xs">
                          <div className="font-medium text-[#12202B] line-clamp-1">{n.title}</div>
                          <div className="text-xs text-[#4A5B68]">
                            Year: {n.year || 'None'} · DOI: {n.doi || 'None'}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#E3F0F5] text-[#0B4A63]">
                            {n.family_label}
                          </span>
                        </td>
                        <td className="py-3 px-4 max-w-xs">
                          {n.parent_title ? (
                            <span className="text-xs italic text-[#12202B] line-clamp-1">{n.parent_title}</span>
                          ) : (
                            <span className="text-xs text-gray-400">None (Root)</span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                              n.confidence_band === 'high'
                                ? 'bg-[#E5F3E8] text-[#1F5429]'
                                : n.confidence_band === 'medium'
                                ? 'bg-[#FFF5E5] text-[#8A5200]'
                                : 'bg-[#FBE4E4] text-[#8A1C1C]'
                            }`}
                          >
                            {n.confidence_band ? n.confidence_band.toUpperCase() : 'N/A'}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-xs">
                          {n.evidence?.cit ?? '-'} / {n.evidence?.sem ?? '-'} / {n.evidence?.kw ?? '-'} /{' '}
                          {n.evidence?.chr ?? '-'}
                        </td>
                        <td className="py-3 px-4">
                          <button
                            onClick={() => setOverrideModal({ open: true, node: n })}
                            className="text-xs text-[#0B5C7A] hover:underline font-semibold"
                          >
                            Override
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* VIEW: MANUSCRIPT POSITIONING */}
          {viewMode === 'positioning' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg border border-[#D7DEE3]">
                <h3 className="font-serif font-bold text-lg text-[#12202B] mb-2">Manuscript Positioning Tool</h3>
                <p className="text-xs text-[#4A5B68] mb-4">
                  Evaluates which research family and candidate parent papers your draft manuscript is closest to in the
                  analyzed set.
                </p>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-[#12202B] mb-1">Manuscript Title</label>
                    <input
                      type="text"
                      value={msTitle}
                      onChange={(e) => setMsTitle(e.target.value)}
                      placeholder="e.g. LLM Clinical Decision Support in Intensive Care"
                      className="w-full text-sm border border-[#D7DEE3] rounded-md px-3 py-2 focus:ring-1 focus:ring-[#0B5C7A]"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#12202B] mb-1">Abstract Text</label>
                    <textarea
                      rows={6}
                      value={msAbstract}
                      onChange={(e) => setMsAbstract(e.target.value)}
                      placeholder="Paste your draft abstract..."
                      className="w-full text-sm border border-[#D7DEE3] rounded-md px-3 py-2 focus:ring-1 focus:ring-[#0B5C7A]"
                    />
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <span className="text-xs text-gray-500">Privacy: Raw text is never retained on disk.</span>
                    <button
                      onClick={handleRunPositioning}
                      disabled={positioningLoading || !msTitle || !msAbstract}
                      className="px-4 py-2 bg-[#0B5C7A] text-white rounded-md text-sm font-semibold hover:bg-[#08455C] disabled:opacity-50"
                    >
                      {positioningLoading ? 'Analyzing...' : 'Position Manuscript'}
                    </button>
                  </div>
                </div>
              </div>

              {/* Positioning Results Drawer */}
              <div className="bg-white p-6 rounded-lg border border-[#D7DEE3]">
                <h4 className="font-serif font-bold text-base text-[#12202B] mb-4">Analysis Results</h4>
                {positioningResult ? (
                  <div className="space-y-4">
                    {/* Persistent Disclaimer Banner */}
                    <div className="p-3 bg-[#E3F0F5] border border-[#B3D6E5] rounded-md text-xs text-[#0B4A63] flex items-start space-x-2">
                      <Compass className="w-4 h-4 shrink-0 mt-0.5" />
                      <span>{positioningResult.disclaimer}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-3 bg-[#F6F8F9] rounded-md border border-[#D7DEE3]">
                        <div className="text-gray-500">Closest Family Branch</div>
                        <div className="font-bold text-sm text-[#0B5C7A] mt-0.5">
                          {positioningResult.closest_family_label}
                        </div>
                      </div>
                      <div className="p-3 bg-[#F6F8F9] rounded-md border border-[#D7DEE3]">
                        <div className="text-gray-500">Overall Fit Quality</div>
                        <div className="font-bold text-sm text-[#12202B] mt-0.5">
                          {positioningResult.fit_label} Fit
                        </div>
                      </div>
                    </div>

                    {/* Top 3 Parent Candidates */}
                    <div>
                      <div className="text-xs font-bold text-[#12202B] mb-2">Top 3 Ancestral Candidate Papers</div>
                      <div className="space-y-2">
                        {positioningResult.top_parents.map((p, idx) => (
                          <div key={idx} className="p-2.5 rounded border border-[#D7DEE3] bg-[#FBFDFD] text-xs">
                            <div className="font-semibold text-[#12202B] line-clamp-1">{p.title}</div>
                            <div className="flex justify-between text-[#4A5B68] mt-1">
                              <span>Published: {p.year || 'Unknown'}</span>
                              <span className="font-mono">Match Score: {Math.round(p.score * 100)}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Shared vs Distinctive Concepts */}
                    <div className="grid grid-cols-2 gap-3 text-xs pt-2">
                      <div>
                        <div className="font-bold text-[#1F5429] mb-1">Shared Concepts (Anchors)</div>
                        <div className="flex flex-wrap gap-1">
                          {positioningResult.shared_concepts.map((c, i) => (
                            <span key={i} className="px-1.5 py-0.5 bg-[#E5F3E8] text-[#1F5429] rounded">
                              {c}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <div className="font-bold text-[#0B5C7A] mb-1">Distinctive Concepts (Delta)</div>
                        <div className="flex flex-wrap gap-1">
                          {positioningResult.distinctive_concepts.map((c, i) => (
                            <span key={i} className="px-1.5 py-0.5 bg-[#E3F0F5] text-[#0B4A63] rounded">
                              {c}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-[#4A5B68] text-sm">
                    Enter title and abstract to run positioning against this lineage tree.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* VIEW: RESEARCH GAPS */}
          {viewMode === 'gaps' && (
            <div className="space-y-4">
              <div className="p-4 bg-[#FFF5E5] border border-[#FAD899] rounded-lg text-xs text-[#8A5200] flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 shrink-0" />
                <span>
                  <strong>Strict Integrity Policy:</strong> Gap signals are extracted directly from in-scope paper
                  limitation sections and leaf nodes. They do NOT constitute global scientific novelty.
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {gaps.map((g) => (
                  <div key={g.id} className="bg-white p-4 rounded-lg border border-[#D7DEE3]">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold uppercase px-2 py-0.5 rounded bg-[#E3F0F5] text-[#0B4A63]">
                        {g.kind.replace('_', ' ')}
                      </span>
                      <span className="text-xs text-gray-500 font-mono">
                        Conf: {Math.round((g.confidence || 0) * 100)}%
                      </span>
                    </div>
                    {g.work_title && <div className="text-xs font-semibold text-[#12202B] mb-2">{g.work_title}</div>}
                    <div className="text-sm italic text-[#4A5B68] bg-[#F6F8F9] p-3 rounded border border-gray-100">
                      "{g.excerpt}"
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-16 bg-white rounded-lg border border-[#D7DEE3]">
          <GitFork className="w-12 h-12 text-[#0B5C7A] mx-auto mb-3" />
          <h3 className="text-lg font-serif font-bold text-[#12202B]">No Lineage DAG Generated Yet</h3>
          <p className="text-sm text-[#4A5B68] max-w-md mx-auto mt-1 mb-6">
            Generate an epistemological parent-child dependency tree from your project library works with verified
            chronology constraints.
          </p>
          <button
            onClick={handleRunLineage}
            disabled={loading}
            className="px-5 py-2.5 bg-[#0B5C7A] text-white rounded-md text-sm font-semibold hover:bg-[#08455C] disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Generate Lineage Tree Now'}
          </button>
        </div>
      )}

      {/* Manual Override Modal */}
      {overrideModal.open && overrideModal.node && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
            <h3 className="font-serif font-bold text-lg text-[#12202B] mb-2">Override Ancestor Parent</h3>
            <p className="text-xs text-[#4A5B68] mb-4">
              Select an alternative candidate paper as the true intellectual ancestor for "{overrideModal.node.title}".
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#12202B] mb-1">New Parent Work</label>
                <select
                  value={newParentId}
                  onChange={(e) => setNewParentId(e.target.value)}
                  className="w-full text-sm border border-[#D7DEE3] rounded-md px-3 py-2 bg-white"
                >
                  <option value="">No Parent (Root Node)</option>
                  {(graph?.nodes || [])
                    .filter((n) => n.work_id !== overrideModal.node?.work_id)
                    .map((n) => (
                      <option key={n.work_id} value={n.work_id}>
                        {n.year ? `(${n.year}) ` : ''}
                        {n.title}
                      </option>
                    ))}
                </select>
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-[#D7DEE3]">
                <button
                  onClick={() => setOverrideModal({ open: false, node: null })}
                  className="px-4 py-2 border border-[#D7DEE3] rounded-md text-sm font-medium hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleApplyOverride}
                  className="px-4 py-2 bg-[#0B5C7A] text-white rounded-md text-sm font-medium hover:bg-[#08455C]"
                >
                  Save Override
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
