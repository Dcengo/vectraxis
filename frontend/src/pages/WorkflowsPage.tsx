import { useState, useEffect } from "react"
import { api, type Workflow } from "../api"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Plus, GitBranch, Trash2, ArrowRight } from "lucide-react"

interface WorkflowsPageProps {
  onOpenBuilder: (workflowId: string | null) => void
}

export function WorkflowsPage({ onOpenBuilder }: WorkflowsPageProps) {
  const [workflows, setWorkflows] = useState<Workflow[]>([])

  useEffect(() => {
    loadWorkflows()
  }, [])

  async function loadWorkflows() {
    try {
      const res = await api.listWorkflows()
      setWorkflows(res.data)
    } catch {
      /* ignore */
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this workflow?")) return
    await api.deleteWorkflow(id)
    await loadWorkflows()
  }

  return (
    <div className="space-y-5 max-w-6xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Workflows</h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Build and manage executable DAG pipelines
          </p>
        </div>
        <Button onClick={() => onOpenBuilder(null)} className="gap-2">
          <Plus className="h-4 w-4" /> New Workflow
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {workflows.map((wf) => (
          <Card
            key={wf.id}
            className="glass glass-hover cursor-pointer group"
            onClick={() => onOpenBuilder(wf.id)}
          >
            <CardContent className="p-5">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  <div className="h-9 w-9 rounded-lg bg-purple-500/10 flex items-center justify-center">
                    <GitBranch className="h-4 w-4 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{wf.name}</p>
                    <p className="text-[11px] text-muted-foreground">v{wf.version}</p>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-red-400 hover:bg-red-500/10"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDelete(wf.id)
                  }}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
              {wf.description && (
                <p className="text-xs text-muted-foreground mb-3 line-clamp-2 leading-relaxed">
                  {wf.description}
                </p>
              )}
              <div className="flex items-center justify-between">
                <div className="flex gap-1.5 flex-wrap">
                  <Badge variant="secondary" className="text-[11px]">
                    {wf.nodes.length} node{wf.nodes.length !== 1 ? "s" : ""}
                  </Badge>
                  {wf.tags.map((t) => (
                    <Badge key={t} variant="outline" className="text-[11px]">
                      {t}
                    </Badge>
                  ))}
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground/40 group-hover:text-primary transition-colors" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {workflows.length === 0 && (
        <Card className="glass">
          <CardContent className="py-16 text-center">
            <div className="h-14 w-14 rounded-xl bg-muted/30 flex items-center justify-center mx-auto mb-4">
              <GitBranch className="h-7 w-7 text-muted-foreground/30" />
            </div>
            <p className="text-sm text-muted-foreground font-medium">
              No workflows yet
            </p>
            <p className="text-xs text-muted-foreground/60 mt-1 mb-4">
              Create your first DAG pipeline to get started
            </p>
            <Button onClick={() => onOpenBuilder(null)} variant="outline" className="gap-2">
              <Plus className="h-4 w-4" /> Create Workflow
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
