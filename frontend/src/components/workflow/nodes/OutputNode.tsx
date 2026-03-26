import { Handle, Position, type NodeProps } from "@xyflow/react"
import { CircleDot } from "lucide-react"

export function OutputNode({ data, selected }: NodeProps) {
  return (
    <div className={`rounded-xl border-2 bg-card/90 backdrop-blur-sm p-3 min-w-[160px] shadow-lg transition-all ${
      selected ? "border-emerald-400 glow-green" : "border-emerald-500/30"
    }`}>
      <Handle type="target" position={Position.Left} className="!bg-emerald-400 !w-2.5 !h-2.5 !border-2 !border-background" />
      <div className="flex items-center gap-2 mb-1">
        <div className="h-5 w-5 rounded bg-emerald-500/20 flex items-center justify-center">
          <CircleDot className="h-3 w-3 text-emerald-400" />
        </div>
        <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider">Output</span>
      </div>
      <div className="text-xs font-medium truncate text-foreground">{(data as Record<string, string>).label || "Output"}</div>
    </div>
  )
}
