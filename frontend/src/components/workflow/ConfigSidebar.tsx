import { useEffect, useState } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { api, type Prompt, type DataSourceInfo } from "../../api"
import type { Node } from "@xyflow/react"
import { Settings2 } from "lucide-react"

interface ConfigSidebarProps {
  node: Node | null
  onConfigChange: (nodeId: string, config: Record<string, unknown>) => void
  onLabelChange: (nodeId: string, label: string) => void
}

export function ConfigSidebar({ node, onConfigChange, onLabelChange }: ConfigSidebarProps) {
  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [dataSources, setDataSources] = useState<DataSourceInfo[]>([])

  useEffect(() => {
    api.listPrompts().then((r) => setPrompts(r.data)).catch(() => {})
    api.dataSources().then((r) => setDataSources(r.data)).catch(() => {})
  }, [])

  if (!node) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-4">
        <div className="h-10 w-10 rounded-lg bg-muted/30 flex items-center justify-center mb-3">
          <Settings2 className="h-5 w-5 text-muted-foreground/30" />
        </div>
        <p className="text-xs text-muted-foreground">Select a node</p>
        <p className="text-[10px] text-muted-foreground/50 mt-0.5">
          Click a node to configure it
        </p>
      </div>
    )
  }

  const config = (node.data as Record<string, unknown>).config as Record<string, unknown> || {}
  const label = (node.data as Record<string, string>).label || ""
  const nodeType = node.type || ""

  function updateConfig(key: string, value: unknown) {
    onConfigChange(node!.id, { ...config, [key]: value })
  }

  return (
    <div className="p-4 space-y-4 overflow-y-auto scrollbar-thin">
      <div>
        <h3 className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-1">
          Configure
        </h3>
        <p className="text-xs text-primary capitalize">{nodeType} Node</p>
      </div>

      <div className="divider" />

      <div className="space-y-1.5">
        <Label className="text-xs">Label</Label>
        <Input
          value={label}
          onChange={(e) => onLabelChange(node.id, e.target.value)}
          placeholder="Node label"
          className="bg-muted/30 border-white/[0.06] h-8 text-xs"
        />
      </div>

      {nodeType === "prompt" && (
        <div className="space-y-1.5">
          <Label className="text-xs">Prompt</Label>
          <select
            value={(config.prompt_id as string) || ""}
            onChange={(e) => updateConfig("prompt_id", e.target.value)}
            className="select-styled text-xs"
          >
            <option value="">Select prompt...</option>
            {prompts.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {nodeType === "condition" && (
        <>
          <div className="space-y-1.5">
            <Label className="text-xs">Field</Label>
            <Input
              value={(config.field as string) || ""}
              onChange={(e) => updateConfig("field", e.target.value)}
              placeholder="e.g. confidence"
              className="bg-muted/30 border-white/[0.06] h-8 text-xs"
            />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Operator</Label>
            <select
              value={(config.operator as string) || "=="}
              onChange={(e) => updateConfig("operator", e.target.value)}
              className="select-styled text-xs"
            >
              <option value=">">&gt;</option>
              <option value="<">&lt;</option>
              <option value="==">==</option>
              <option value="!=">!=</option>
              <option value="contains">contains</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Value</Label>
            <Input
              value={(config.value as string) || ""}
              onChange={(e) => updateConfig("value", e.target.value)}
              placeholder="0.8"
              className="bg-muted/30 border-white/[0.06] h-8 text-xs font-mono"
            />
          </div>
        </>
      )}

      {nodeType === "data_source" && (
        <div className="space-y-1.5">
          <Label className="text-xs">Data Source</Label>
          <select
            value={(config.data_source_id as string) || ""}
            onChange={(e) => updateConfig("data_source_id", e.target.value)}
            className="select-styled text-xs"
          >
            <option value="">Select data source...</option>
            {dataSources.map((ds) => (
              <option key={ds.id} value={ds.id}>
                {ds.name} ({ds.record_count} records)
              </option>
            ))}
          </select>
        </div>
      )}

      {nodeType === "validator" && (
        <>
          <div className="space-y-1.5">
            <Label className="text-xs">Validator Type</Label>
            <select
              value={(config.validator_type as string) || "structure"}
              onChange={(e) => updateConfig("validator_type", e.target.value)}
              className="select-styled text-xs"
            >
              <option value="structure">Structure</option>
              <option value="faithfulness">Faithfulness</option>
            </select>
          </div>
          {(config.validator_type || "structure") === "structure" && (
            <div className="space-y-1.5">
              <Label className="text-xs">Min Length</Label>
              <Input
                type="number"
                value={(config.min_length as number) || 10}
                onChange={(e) =>
                  updateConfig("min_length", parseInt(e.target.value) || 10)
                }
                className="bg-muted/30 border-white/[0.06] h-8 text-xs font-mono"
              />
            </div>
          )}
        </>
      )}

      {nodeType === "merger" && (
        <div className="space-y-1.5">
          <Label className="text-xs">Strategy</Label>
          <select
            value={(config.strategy as string) || "concatenate"}
            onChange={(e) => updateConfig("strategy", e.target.value)}
            className="select-styled text-xs"
          >
            <option value="concatenate">Concatenate</option>
            <option value="summarize">Summarize</option>
          </select>
        </div>
      )}

      {nodeType === "output" && (
        <div className="space-y-1.5">
          <Label className="text-xs">Format</Label>
          <select
            value={(config.format as string) || "text"}
            onChange={(e) => updateConfig("format", e.target.value)}
            className="select-styled text-xs"
          >
            <option value="text">Text</option>
            <option value="json">JSON</option>
          </select>
        </div>
      )}
    </div>
  )
}
