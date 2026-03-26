import { Handle, Position, type NodeProps } from "@xyflow/react"
import { Merge } from "lucide-react"

export function MergerNode({ data, selected }: NodeProps) {
  return (
    <div className={`rounded-xl border-2 bg-card/90 backdrop-blur-sm p-3 min-w-[160px] shadow-lg transition-all ${
      selected ? "border-cyan-400 glow-cyan" : "border-cyan-500/30"
    }`}>
      <Handle type="target" position={Position.Left} className="!bg-cyan-400 !w-2.5 !h-2.5 !border-2 !border-background" />
      <div className="flex items-center gap-2 mb-1">
        <div className="h-5 w-5 rounded bg-cyan-500/20 flex items-center justify-center">
          <Merge className="h-3 w-3 text-cyan-400" />
        </div>
        <span className="text-[10px] font-semibold text-cyan-400 uppercase tracking-wider">Merger</span>
      </div>
      <div className="text-xs font-medium truncate text-foreground">{(data as Record<string, string>).label || "Merger"}</div>
      <Handle type="source" position={Position.Right} className="!bg-cyan-400 !w-2.5 !h-2.5 !border-2 !border-background" />
    </div>
  )
}
