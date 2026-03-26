import { Handle, Position, type NodeProps } from "@xyflow/react"
import { GitFork } from "lucide-react"

export function ConditionNode({ data, selected }: NodeProps) {
  return (
    <div className={`rounded-xl border-2 bg-card/90 backdrop-blur-sm p-3 min-w-[160px] shadow-lg transition-all ${
      selected ? "border-yellow-400 glow-purple" : "border-yellow-500/30"
    }`}>
      <Handle type="target" position={Position.Left} className="!bg-yellow-400 !w-2.5 !h-2.5 !border-2 !border-background" />
      <div className="flex items-center gap-2 mb-1">
        <div className="h-5 w-5 rounded bg-yellow-500/20 flex items-center justify-center">
          <GitFork className="h-3 w-3 text-yellow-400" />
        </div>
        <span className="text-[10px] font-semibold text-yellow-400 uppercase tracking-wider">Condition</span>
      </div>
      <div className="text-xs font-medium truncate text-foreground">{(data as Record<string, string>).label || "Condition"}</div>
      <Handle
        type="source"
        position={Position.Right}
        id="true"
        className="!bg-emerald-400 !w-2.5 !h-2.5 !border-2 !border-background"
        style={{ top: "35%" }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="false"
        className="!bg-red-400 !w-2.5 !h-2.5 !border-2 !border-background"
        style={{ top: "70%" }}
      />
      <div className="absolute -right-9 top-[28%] text-[9px] font-semibold text-emerald-400 bg-emerald-400/10 px-1 rounded">
        T
      </div>
      <div className="absolute -right-9 top-[63%] text-[9px] font-semibold text-red-400 bg-red-400/10 px-1 rounded">
        F
      </div>
    </div>
  )
}
