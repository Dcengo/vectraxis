import axios from 'axios'

const client = axios.create({ baseURL: '/api/v1' })

export interface HealthResponse {
  status: string
  version: string
}

export interface PipelineInfo {
  name: string
  description: string
  agent_types: string[]
}

export interface ModelInfo {
  model: string
  provider: string
  status: string
}

export interface ProviderInfo {
  name: string
  status: string
  models: string[]
}

export interface QueryRequest {
  query: string
  agent_type: string
  model?: string
}

export interface QueryResponse {
  query: string
  output: string
  confidence: number
  agent_type: string
  steps: string[]
  model: string
}

export interface IngestResponse {
  source_id: string
  records_count: number
  message: string
}

export interface EvaluationStatus {
  available_metrics: string[]
  status: string
}

export interface DataSourceInfo {
  id: string
  name: string
  source_type: string
  record_count: number
}

export interface DataSourceRef {
  data_source_id: string
  data_source_name: string
}

export interface ChatRequest {
  message: string
  data_sources: DataSourceRef[]
  model?: string
  agent_type?: string
}

export interface ChatResponse {
  message: string
  response: string
  confidence: number
  data_sources_used: { id: string; name: string }[]
  steps: string[]
  model: string
}

// Prompt types
export interface Prompt {
  id: string
  name: string
  description: string
  system_prompt: string
  user_prompt_template: string
  model: string
  agent_type: string
  output_json_schema: Record<string, unknown> | null
  temperature: number
  max_tokens: number
  variables: string[]
  tags: string[]
  version: number
  created_at: string | null
  updated_at: string | null
}

export interface PromptCreate {
  name: string
  description?: string
  system_prompt?: string
  user_prompt_template: string
  model?: string
  agent_type?: string
  output_json_schema?: Record<string, unknown> | null
  temperature?: number
  max_tokens?: number
  variables?: string[]
  tags?: string[]
}

export interface PromptUpdate {
  name?: string
  description?: string
  system_prompt?: string
  user_prompt_template?: string
  model?: string
  agent_type?: string
  output_json_schema?: Record<string, unknown> | null
  temperature?: number
  max_tokens?: number
  variables?: string[]
  tags?: string[]
}

// Workflow types
export interface WorkflowNode {
  id: string
  type: string
  label: string
  position: { x: number; y: number }
  config: Record<string, unknown>
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  source_handle?: string | null
  label: string
}

export interface Workflow {
  id: string
  name: string
  description: string
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  tags: string[]
  version: number
  created_at: string | null
  updated_at: string | null
}

export interface WorkflowCreate {
  name: string
  description?: string
  nodes?: WorkflowNode[]
  edges?: WorkflowEdge[]
  tags?: string[]
}

export interface WorkflowUpdate {
  name?: string
  description?: string
  nodes?: WorkflowNode[]
  edges?: WorkflowEdge[]
  tags?: string[]
}

export interface NodeExecutionResult {
  node_id: string
  node_type: string
  status: string
  output: string
  error: string | null
  duration_ms: number
}

export interface WorkflowRunResult {
  id: string
  workflow_id: string
  status: string
  node_results: NodeExecutionResult[]
  final_output: string
  error: string | null
  duration_ms: number
}

export const api = {
  health: () => client.get<HealthResponse>('/health'),
  pipelines: () => client.get<PipelineInfo[]>('/pipelines/'),
  models: () => client.get<ModelInfo[]>('/models/'),
  providers: () => client.get<ProviderInfo[]>('/providers/'),
  query: (data: QueryRequest) => client.post<QueryResponse>('/query/', data),
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return client.post<IngestResponse>('/ingestion/upload', form)
  },
  evaluationStatus: () => client.get<EvaluationStatus>('/evaluation/status'),
  dataSources: () => client.get<DataSourceInfo[]>('/data-sources/'),
  chat: (data: ChatRequest) => client.post<ChatResponse>('/chat/', data),

  // Prompts
  createPrompt: (data: PromptCreate) => client.post<Prompt>('/prompts/', data),
  listPrompts: (tags?: string) =>
    client.get<Prompt[]>('/prompts/', { params: tags ? { tags } : {} }),
  getPrompt: (id: string) => client.get<Prompt>(`/prompts/${id}`),
  updatePrompt: (id: string, data: PromptUpdate) =>
    client.put<Prompt>(`/prompts/${id}`, data),
  deletePrompt: (id: string) => client.delete(`/prompts/${id}`),

  // Workflows
  createWorkflow: (data: WorkflowCreate) =>
    client.post<Workflow>('/workflows/', data),
  listWorkflows: () => client.get<Workflow[]>('/workflows/'),
  getWorkflow: (id: string) => client.get<Workflow>(`/workflows/${id}`),
  updateWorkflow: (id: string, data: WorkflowUpdate) =>
    client.put<Workflow>(`/workflows/${id}`, data),
  deleteWorkflow: (id: string) => client.delete(`/workflows/${id}`),
  runWorkflow: (id: string) =>
    client.post<WorkflowRunResult>(`/workflows/${id}/run`),
}
