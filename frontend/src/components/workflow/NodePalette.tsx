import {
  FileText,
  GitFork,
  Database,
  ShieldCheck,
  Merge,
  CircleDot,
} from "lucide-react"

const NODE_TYPES = [
  { type: "prompt", label: "Prompt", color: "bg-purple-500/10 text-purple-400 border-purple-500/30", icon: FileText },
  { type: "condition", label: "Condition", color: "bg-yellow-500/10 text-yellow-400 border-yellow-500/30", icon: GitFork },
  { type: "data_source", label: "Data Source", color: "bg-blue-500/10 text-blue-400 border-blue-500/30", icon: Database },
  { type: "validator", label: "Validator", color: "bg-orange-500/10 text-orange-400 border-orange-500/30", icon: ShieldCheck },
  { type: "merger", label: "Merger", color: "bg-cyan-500/10 text-cyan-400 border-cyan-500/30", icon: Merge },
  { type: "output", label: "Output", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30", icon: CircleDot },
]

export function NodePalette() {
  function onDragStart(event: React.DragEvent, nodeType: string, label: string) {
    event.dataTransfer.setData("application/reactflow-type", nodeType)
    event.dataTransfer.setData("application/reactflow-label", label)
    event.dataTransfer.effectAllowed = "move"
  }

  return (
    <div className="p-3 space-y-1.5">
      <h3 className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider px-1 mb-3">
        Nodes
      </h3>
      {NODE_TYPES.map((nt) => {
        const Icon = nt.icon
        return (
          <div
            key={nt.type}
            draggable
            onDragStart={(e) => onDragStart(e, nt.type, nt.label)}
            className={`flex items-center gap-2.5 rounded-lg border ${nt.color} p-2.5 text-xs font-medium cursor-grab active:cursor-grabbing hover:brightness-125 transition-all`}
          >
            <Icon className="h-3.5 w-3.5 shrink-0" />
            {nt.label}
          </div>
        )
      })}
      <p className="text-[10px] text-muted-foreground/50 px-1 pt-2">
        Drag to canvas
      </p>
    </div>
  )
}
