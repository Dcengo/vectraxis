import { useState, useEffect } from "react"
import {
  api,
  type HealthResponse,
  type PipelineInfo,
  type QueryResponse,
  type IngestResponse,
  type EvaluationStatus,
  type ModelInfo,
  type ProviderInfo,
  type DataSourceInfo,
} from "./api"
import { ChatPanel } from "./components/ChatPanel"
import { NavBar, type Page } from "./components/NavBar"
import { PromptsPage } from "./pages/PromptsPage"
import { WorkflowsPage } from "./pages/WorkflowsPage"
import { WorkflowBuilderPage } from "./pages/WorkflowBuilderPage"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Activity,
  Upload,
  Search,
  GitBranch,
  BarChart3,
  CheckCircle2,
  XCircle,
  Loader2,
  Cpu,
  Server,
  Zap,
  Database,
  ArrowRight,
} from "lucide-react"

function App() {
  const [page, setPage] = useState<Page>("dashboard")
  const [builderWorkflowId, setBuilderWorkflowId] = useState<string | null>(null)
  const [showBuilder, setShowBuilder] = useState(false)

  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [pipelines, setPipelines] = useState<PipelineInfo[]>([])
  const [evalStatus, setEvalStatus] = useState<EvaluationStatus | null>(null)
  const [models, setModels] = useState<ModelInfo[]>([])
  const [providers, setProviders] = useState<ProviderInfo[]>([])
  const [dataSources, setDataSources] = useState<DataSourceInfo[]>([])

  const [queryText, setQueryText] = useState("")
  const [agentType, setAgentType] = useState("analysis")
  const [selectedModel, setSelectedModel] = useState("")
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null)
  const [queryLoading, setQueryLoading] = useState(false)

  const [uploadResult, setUploadResult] = useState<IngestResponse | null>(null)
  const [uploadLoading, setUploadLoading] = useState(false)

  const [error, setError] = useState("")

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      const [h, p, e, m, prov] = await Promise.all([
        api.health(),
        api.pipelines(),
        api.evaluationStatus(),
        api.models(),
        api.providers(),
      ])
      setHealth(h.data)
      setPipelines(p.data)
      setEvalStatus(e.data)
      setModels(m.data)
      setProviders(prov.data)
      setError("")
    } catch {
      setError("Failed to connect to API. Is the backend running?")
    }
    try {
      const ds = await api.dataSources()
      setDataSources(ds.data)
    } catch {
      // Data sources endpoint may not be available yet
    }
  }

  async function handleQuery() {
    if (!queryText.trim()) return
    setQueryLoading(true)
    setQueryResult(null)
    setError("")
    try {
      const req: { query: string; agent_type: string; model?: string } = {
        query: queryText,
        agent_type: agentType,
      }
      if (selectedModel) {
        req.model = selectedModel
      }
      const res = await api.query(req)
      setQueryResult(res.data)
    } catch {
      setError("Query failed")
    } finally {
      setQueryLoading(false)
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadLoading(true)
    setUploadResult(null)
    setError("")
    try {
      const res = await api.upload(file)
      setUploadResult(res.data)
      try {
        const dsRes = await api.dataSources()
        setDataSources(dsRes.data)
      } catch {
        // Data sources endpoint may not be available
      }
    } catch {
      setError("Upload failed")
    } finally {
      setUploadLoading(false)
    }
  }

  const activeModels = models.filter((m) => m.status === "active")
  const modelsByProvider: Record<string, ModelInfo[]> = {}
  for (const m of activeModels) {
    if (!modelsByProvider[m.provider]) modelsByProvider[m.provider] = []
    modelsByProvider[m.provider].push(m)
  }

  function openBuilder(workflowId: string | null) {
    setBuilderWorkflowId(workflowId)
    setShowBuilder(true)
  }

  function closeBuilder() {
    setShowBuilder(false)
    setBuilderWorkflowId(null)
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <NavBar
        activePage={page}
        onPageChange={(p) => {
          setPage(p)
          if (showBuilder) closeBuilder()
        }}
      />

      {/* Main content area */}
      <main className="flex-1 overflow-y-auto scrollbar-thin">
        {/* Top bar */}
        <header className="sticky top-0 z-30 flex items-center justify-between h-14 px-6 border-b border-white/[0.06] bg-background/80 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-foreground capitalize">
              {page === "workflows" && showBuilder ? "Workflow Builder" : page}
            </h2>
            {health && (
              <div className="flex items-center gap-1.5">
                <div className={`status-dot ${health.status === "healthy" ? "status-dot-active" : "status-dot-inactive"}`} />
                <span className="text-xs text-muted-foreground">
                  v{health.version}
                </span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-3">
            {providers.filter((p) => p.status === "active").length > 0 && (
              <div className="flex items-center gap-1.5">
                <Zap className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-xs text-muted-foreground">
                  {providers.filter((p) => p.status === "active").length} provider{providers.filter((p) => p.status === "active").length !== 1 ? "s" : ""} active
                </span>
              </div>
            )}
          </div>
        </header>

        {/* Error banner */}
        {error && (
          <div className="mx-6 mt-4 flex items-center gap-2.5 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            <XCircle className="h-4 w-4 shrink-0" />
            {error}
            <button
              onClick={() => setError("")}
              className="ml-auto text-red-400/60 hover:text-red-400"
            >
              <XCircle className="h-3.5 w-3.5" />
            </button>
          </div>
        )}

        {/* Page content */}
        <div className="p-6">
          {page === "prompts" && (
            <div className="page-enter">
              <PromptsPage />
            </div>
          )}

          {page === "workflows" && showBuilder && (
            <div className="page-enter">
              <WorkflowBuilderPage
                workflowId={builderWorkflowId}
                onBack={closeBuilder}
              />
            </div>
          )}

          {page === "workflows" && !showBuilder && (
            <div className="page-enter">
              <WorkflowsPage onOpenBuilder={openBuilder} />
            </div>
          )}

          {page === "dashboard" && (
            <div className="page-enter space-y-6 max-w-6xl">
              {/* Metric cards row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Health */}
                <div className="metric-card">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-emerald-500/10">
                      <Activity className="h-4 w-4 text-emerald-400" />
                    </div>
                    {health && (
                      <div className={`status-dot ${health.status === "healthy" ? "status-dot-active" : "status-dot-inactive"}`} />
                    )}
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">API Status</p>
                    <p className="text-lg font-semibold capitalize">
                      {health?.status || "Connecting..."}
                    </p>
                  </div>
                </div>

                {/* Models */}
                <div className="metric-card">
                  <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-purple-500/10">
                    <Cpu className="h-4 w-4 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Active Models</p>
                    <p className="text-lg font-semibold">
                      {activeModels.length}
                      <span className="text-sm font-normal text-muted-foreground">
                        {" "}/ {models.length}
                      </span>
                    </p>
                  </div>
                </div>

                {/* Pipelines */}
                <div className="metric-card">
                  <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-cyan-500/10">
                    <GitBranch className="h-4 w-4 text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Pipelines</p>
                    <p className="text-lg font-semibold">{pipelines.length}</p>
                  </div>
                </div>

                {/* Data Sources */}
                <div className="metric-card">
                  <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-amber-500/10">
                    <Database className="h-4 w-4 text-amber-400" />
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Data Sources</p>
                    <p className="text-lg font-semibold">{dataSources.length}</p>
                  </div>
                </div>
              </div>

              {/* Providers + Evaluation row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Providers */}
                <Card className="glass lg:col-span-2">
                  <CardHeader className="flex flex-row items-center justify-between pb-3">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <Server className="h-4 w-4 text-purple-400" />
                      Providers
                    </CardTitle>
                    <Badge variant="secondary" className="text-xs">
                      {providers.filter((p) => p.status === "active").length} active
                    </Badge>
                  </CardHeader>
                  <CardContent>
                    {providers.length > 0 ? (
                      <div className="space-y-2">
                        {providers.map((p) => (
                          <div
                            key={p.name}
                            className="flex items-center justify-between rounded-lg bg-muted/30 px-4 py-3 transition-colors hover:bg-muted/50"
                          >
                            <div className="flex items-center gap-3">
                              <div className={`status-dot ${p.status === "active" ? "status-dot-active" : "status-dot-inactive"}`} />
                              <p className="font-medium text-sm capitalize">{p.name}</p>
                            </div>
                            <div className="flex gap-1.5 flex-wrap justify-end">
                              {p.models.map((m) => (
                                <Badge key={m} variant="outline" className="text-[11px] font-mono">
                                  {m}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-muted-foreground">Loading...</p>
                    )}
                  </CardContent>
                </Card>

                {/* Evaluation + Pipelines */}
                <div className="space-y-4">
                  <Card className="glass">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <BarChart3 className="h-4 w-4 text-cyan-400" />
                        Evaluation
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {evalStatus ? (
                        <div className="space-y-2">
                          <Badge variant="secondary" className="text-xs">{evalStatus.status}</Badge>
                          <div className="flex flex-wrap gap-1">
                            {evalStatus.available_metrics.map((m) => (
                              <Badge key={m} variant="outline" className="text-[11px]">
                                {m}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <p className="text-xs text-muted-foreground">Loading...</p>
                      )}
                    </CardContent>
                  </Card>

                  <Card className="glass">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <GitBranch className="h-4 w-4 text-purple-400" />
                        Pipelines
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {pipelines.length > 0 ? (
                        <div className="space-y-2">
                          {pipelines.map((p) => (
                            <div
                              key={p.name}
                              className="rounded-lg bg-muted/30 px-3 py-2.5"
                            >
                              <p className="text-sm font-medium">{p.name}</p>
                              <div className="flex gap-1 mt-1">
                                {p.agent_types.map((t) => (
                                  <Badge key={t} variant="outline" className="text-[11px]">
                                    {t}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-muted-foreground">Loading...</p>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* Query */}
              <Card className="glass gradient-border">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Search className="h-4 w-4 text-cyan-400" />
                    Query Pipeline
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2.5">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        value={queryText}
                        onChange={(e) => setQueryText(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleQuery()}
                        placeholder="Ask your data anything..."
                        className="pl-9 h-10 bg-muted/30 border-white/[0.06]"
                      />
                    </div>
                    <select
                      value={agentType}
                      onChange={(e) => setAgentType(e.target.value)}
                      className="select-styled w-[150px]"
                    >
                      <option value="analysis">Analysis</option>
                      <option value="summarization">Summarization</option>
                      <option value="recommendation">Recommendation</option>
                    </select>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="select-styled w-[180px]"
                    >
                      <option value="">Default model</option>
                      {Object.entries(modelsByProvider).map(([provider, provModels]) => (
                        <optgroup key={provider} label={provider}>
                          {provModels.map((m) => (
                            <option key={m.model} value={m.model}>
                              {m.model}
                            </option>
                          ))}
                        </optgroup>
                      ))}
                    </select>
                    <Button onClick={handleQuery} disabled={queryLoading} className="gap-2">
                      {queryLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          Run
                          <ArrowRight className="h-3.5 w-3.5" />
                        </>
                      )}
                    </Button>
                  </div>

                  {queryResult && (
                    <div className="space-y-3 rounded-xl bg-muted/20 border border-white/[0.04] p-5">
                      <div>
                        <p className="text-xs font-medium text-muted-foreground mb-1.5">Output</p>
                        <p className="text-sm leading-relaxed">{queryResult.output}</p>
                      </div>
                      <div className="divider" />
                      <div className="flex gap-5">
                        <div>
                          <p className="text-[11px] text-muted-foreground mb-0.5">Confidence</p>
                          <p className="text-sm font-mono font-semibold text-emerald-400">
                            {(queryResult.confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                        <div>
                          <p className="text-[11px] text-muted-foreground mb-0.5">Agent</p>
                          <Badge variant="outline" className="text-xs">
                            {queryResult.agent_type}
                          </Badge>
                        </div>
                        <div>
                          <p className="text-[11px] text-muted-foreground mb-0.5">Model</p>
                          <Badge variant="outline" className="text-xs font-mono">
                            <Cpu className="mr-1 inline h-3 w-3" />
                            {queryResult.model}
                          </Badge>
                        </div>
                      </div>
                      {queryResult.steps.length > 0 && (
                        <>
                          <div className="divider" />
                          <div>
                            <p className="text-[11px] text-muted-foreground mb-1.5">Pipeline Steps</p>
                            <ol className="list-decimal list-inside text-sm space-y-1 text-muted-foreground">
                              {queryResult.steps.map((s, i) => (
                                <li key={i}>{s}</li>
                              ))}
                            </ol>
                          </div>
                        </>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Upload */}
              <Card className="glass">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Upload className="h-4 w-4 text-purple-400" />
                    Upload Data
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <label className="flex items-center justify-center gap-3 rounded-xl border-2 border-dashed border-white/[0.08] bg-muted/20 py-8 cursor-pointer transition-colors hover:border-primary/30 hover:bg-muted/30">
                    <input
                      type="file"
                      onChange={handleUpload}
                      accept=".csv,.json,.txt,.docx"
                      disabled={uploadLoading}
                      className="hidden"
                    />
                    {uploadLoading ? (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Loader2 className="h-5 w-5 animate-spin text-primary" />
                        Processing file...
                      </div>
                    ) : (
                      <div className="text-center">
                        <Upload className="h-8 w-8 text-muted-foreground/50 mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground">
                          Drop a file or <span className="text-primary">browse</span>
                        </p>
                        <p className="text-xs text-muted-foreground/60 mt-1">
                          CSV, JSON, TXT, DOCX
                        </p>
                      </div>
                    )}
                  </label>
                  {uploadResult && (
                    <div className="flex items-start gap-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-4">
                      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                      <div className="text-sm space-y-1">
                        <p className="text-emerald-300">{uploadResult.message}</p>
                        <div className="flex gap-3 text-xs text-muted-foreground font-mono">
                          <span>ID: {uploadResult.source_id}</span>
                          <span>Records: {uploadResult.records_count}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Chat */}
              <ChatPanel
                dataSources={dataSources}
                models={models}
                selectedModel={selectedModel}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
