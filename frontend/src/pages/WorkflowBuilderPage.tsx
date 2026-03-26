import { useState, useEffect, useCallback } from "react"
import type { Node, Edge } from "@xyflow/react"
import { api, type WorkflowRunResult } from "../api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { WorkflowCanvas, updateNodeData } from "@/components/workflow/WorkflowCanvas"
import { NodePalette } from "@/components/workflow/NodePalette"
import { ConfigSidebar } from "@/components/workflow/ConfigSidebar"
import { RunResultsPanel } from "@/components/workflow/RunResultsPanel"
import { ArrowLeft, Play, Save, Loader2 } from "lucide-react"

interface WorkflowBuilderPageProps {
  workflowId: string | null
  onBack: () => void
}

export function WorkflowBuilderPage({
  workflowId,
  onBack,
}: WorkflowBuilderPageProps) {
  const [name, setName] = useState("Untitled Workflow")
  const [description, setDescription] = useState("")
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [runResult, setRunResult] = useState<WorkflowRunResult | null>(null)
  const [saving, setSaving] = useState(false)
  const [running, setRunning] = useState(false)
  const [currentId, setCurrentId] = useState<string | null>(workflowId)

  useEffect(() => {
    if (workflowId) {
      api.getWorkflow(workflowId).then((res) => {
        const wf = res.data
        setName(wf.name)
        setDescription(wf.description)
        setCurrentId(wf.id)
        setNodes(
          wf.nodes.map((n) => ({
            id: n.id,
            type: n.type,
            position: n.position,
            data: { label: n.label, config: n.config },
          }))
        )
        setEdges(
          wf.edges.map((e) => ({
            id: e.id,
            source: e.source,
            target: e.target,
            sourceHandle: e.source_handle || undefined,
            label: e.label,
          }))
        )
      }).catch(() => {})
    }
  }, [workflowId])

  const handleSave = useCallback(async () => {
    setSaving(true)
    try {
      const wfNodes = nodes.map((n) => ({
        id: n.id,
        type: n.type || "output",
        label: (n.data as Record<string, string>).label || "",
        position: n.position,
        config: ((n.data as Record<string, unknown>).config as Record<string, unknown>) || {},
      }))
      const wfEdges = edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        source_handle: (e.sourceHandle as string) || null,
        label: (e.label as string) || "",
      }))

      if (currentId) {
        await api.updateWorkflow(currentId, {
          name,
          description,
          nodes: wfNodes,
          edges: wfEdges,
        })
      } else {
        const res = await api.createWorkflow({
          name,
          description,
          nodes: wfNodes,
          edges: wfEdges,
        })
        setCurrentId(res.data.id)
      }
    } catch {
      alert("Save failed")
    }
    setSaving(false)
  }, [nodes, edges, name, description, currentId])

  const handleRun = useCallback(async () => {
    if (!currentId) {
      alert("Save the workflow first")
      return
    }
    setRunning(true)
    setRunResult(null)
    try {
      await handleSave()
      const res = await api.runWorkflow(currentId)
      setRunResult(res.data)
    } catch {
      alert("Run failed")
    }
    setRunning(false)
  }, [currentId, handleSave])

  function handleConfigChange(nodeId: string, config: Record<string, unknown>) {
    setNodes((nds) => updateNodeData(nds, nodeId, { config }))
    if (selectedNode?.id === nodeId) {
      setSelectedNode((prev) =>
        prev
          ? { ...prev, data: { ...prev.data, config } }
          : null
      )
    }
  }

  function handleLabelChange(nodeId: string, label: string) {
    setNodes((nds) => updateNodeData(nds, nodeId, { label }))
    if (selectedNode?.id === nodeId) {
      setSelectedNode((prev) =>
        prev ? { ...prev, data: { ...prev.data, label } } : null
      )
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Toolbar */}
      <div className="flex items-center gap-3 pb-3 mb-3 border-b border-white/[0.06]">
        <Button size="sm" variant="ghost" onClick={onBack} className="h-8 w-8 p-0">
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="h-5 w-px bg-border" />
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="max-w-[260px] h-8 font-medium bg-muted/30 border-white/[0.06]"
          placeholder="Workflow name"
        />
        <Input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="max-w-[300px] h-8 text-sm bg-muted/30 border-white/[0.06]"
          placeholder="Description (optional)"
        />
        <div className="flex-1" />
        <Button size="sm" variant="outline" onClick={handleSave} disabled={saving} className="h-8 text-xs gap-1.5">
          {saving ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Save className="h-3.5 w-3.5" />
          )}
          Save
        </Button>
        <Button size="sm" onClick={handleRun} disabled={running} className="h-8 text-xs gap-1.5">
          {running ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Play className="h-3.5 w-3.5" />
          )}
          Run
        </Button>
      </div>

      {/* Main layout */}
      <div className="flex flex-1 gap-0 min-h-0 rounded-xl border border-white/[0.06] overflow-hidden">
        {/* Node Palette */}
        <div className="w-[150px] border-r border-white/[0.06] bg-card/30 overflow-y-auto scrollbar-thin shrink-0">
          <NodePalette />
        </div>

        {/* Canvas */}
        <div className="flex-1 min-w-0">
          <WorkflowCanvas
            initialNodes={nodes}
            initialEdges={edges}
            onNodesChange={setNodes}
            onEdgesChange={setEdges}
            onNodeSelect={setSelectedNode}
          />
        </div>

        {/* Config Sidebar */}
        <div className="w-[260px] border-l border-white/[0.06] bg-card/30 overflow-y-auto scrollbar-thin shrink-0">
          <ConfigSidebar
            node={selectedNode}
            onConfigChange={handleConfigChange}
            onLabelChange={handleLabelChange}
          />
        </div>
      </div>

      {/* Run Results */}
      <RunResultsPanel result={runResult} />
    </div>
  )
}
