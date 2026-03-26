import type { WorkflowRunResult } from "../../api"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, XCircle, MinusCircle, Clock } from "lucide-react"

interface RunResultsPanelProps {
  result: WorkflowRunResult | null
}

export function RunResultsPanel({ result }: RunResultsPanelProps) {
  if (!result) return null

  const statusIcon = result.status === "completed"
    ? <CheckCircle2 className="h-4 w-4 text-emerald-400" />
    : <XCircle className="h-4 w-4 text-red-400" />

  return (
    <div className="mt-3 rounded-xl border border-white/[0.06] bg-card/40 backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2.5">
          {statusIcon}
          <h3 className="text-sm font-semibold">Run Results</h3>
        </div>
        <div className="flex items-center gap-3">
          <Badge
            variant={result.status === "completed" ? "default" : "destructive"}
            className="text-[11px]"
          >
            {result.status}
          </Badge>
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            {result.duration_ms.toFixed(0)}ms
          </div>
        </div>
      </div>

      <div className="p-4 space-y-3 max-h-[250px] overflow-y-auto scrollbar-thin">
        {result.error && (
          <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            {result.error}
          </div>
        )}

        {result.final_output && (
          <div>
            <p className="text-[11px] font-medium text-muted-foreground mb-1.5">
              Final Output
            </p>
            <pre className="text-xs bg-muted/20 border border-white/[0.04] rounded-lg p-3 whitespace-pre-wrap max-h-[100px] overflow-y-auto scrollbar-thin font-mono">
              {result.final_output}
            </pre>
          </div>
        )}

        <div>
          <p className="text-[11px] font-medium text-muted-foreground mb-2">
            Node Results
          </p>
          <div className="space-y-1.5">
            {result.node_results.map((nr) => (
              <div
                key={nr.node_id}
                className="flex items-center justify-between text-xs rounded-lg bg-muted/20 px-3 py-2"
              >
                <div className="flex items-center gap-2">
                  {nr.status === "completed" ? (
                    <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                  ) : nr.status === "skipped" ? (
                    <MinusCircle className="h-3 w-3 text-muted-foreground" />
                  ) : (
                    <XCircle className="h-3 w-3 text-red-400" />
                  )}
                  <span className="font-medium font-mono">{nr.node_id}</span>
                  <span className="text-muted-foreground">({nr.node_type})</span>
                </div>
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Clock className="h-2.5 w-2.5" />
                  {nr.duration_ms.toFixed(0)}ms
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
