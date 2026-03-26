import { Handle, Position, type NodeProps } from "@xyflow/react"
import { Database } from "lucide-react"

export function DataSourceNode({ data, selected }: NodeProps) {
  return (
    <div className={`rounded-xl border-2 bg-card/90 backdrop-blur-sm p-3 min-w-[160px] shadow-lg transition-all ${
      selected ? "border-blue-400 glow-cyan" : "border-blue-500/30"
    }`}>
      <div className="flex items-center gap-2 mb-1">
        <div className="h-5 w-5 rounded bg-blue-500/20 flex items-center justify-center">
          <Database className="h-3 w-3 text-blue-400" />
        </div>
        <span className="text-[10px] font-semibold text-blue-400 uppercase tracking-wider">Data Source</span>
      </div>
      <div className="text-xs font-medium truncate text-foreground">{(data as Record<string, string>).label || "Data Source"}</div>
      <Handle type="source" position={Position.Right} className="!bg-blue-400 !w-2.5 !h-2.5 !border-2 !border-background" />
    </div>
  )
}
