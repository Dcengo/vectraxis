import { Handle, Position, type NodeProps } from "@xyflow/react"
import { FileText } from "lucide-react"

export function PromptNode({ data, selected }: NodeProps) {
  return (
    <div className={`rounded-xl border-2 bg-card/90 backdrop-blur-sm p-3 min-w-[160px] shadow-lg transition-all ${
      selected ? "border-purple-400 glow-purple" : "border-purple-500/30"
    }`}>
      <Handle type="target" position={Position.Left} className="!bg-purple-400 !w-2.5 !h-2.5 !border-2 !border-background" />
      <div className="flex items-center gap-2 mb-1">
        <div className="h-5 w-5 rounded bg-purple-500/20 flex items-center justify-center">
          <FileText className="h-3 w-3 text-purple-400" />
        </div>
        <span className="text-[10px] font-semibold text-purple-400 uppercase tracking-wider">Prompt</span>
      </div>
      <div className="text-xs font-medium truncate text-foreground">{(data as Record<string, string>).label || "Prompt"}</div>
      <Handle type="source" position={Position.Right} className="!bg-purple-400 !w-2.5 !h-2.5 !border-2 !border-background" />
    </div>
  )
}
