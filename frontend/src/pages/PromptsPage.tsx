import { useState, useEffect, useCallback } from "react"
import { api, type Prompt, type PromptCreate, type ModelInfo } from "../api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Plus, Trash2, Copy, Save, Loader2, FileText, X } from "lucide-react"

export function PromptsPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [selected, setSelected] = useState<Prompt | null>(null)
  const [models, setModels] = useState<ModelInfo[]>([])
  const [saving, setSaving] = useState(false)
  const [tagInput, setTagInput] = useState("")

  const [form, setForm] = useState<PromptCreate>({
    name: "",
    user_prompt_template: "",
    description: "",
    system_prompt: "",
    model: "",
    agent_type: "analysis",
    output_json_schema: null,
    temperature: 0.7,
    max_tokens: 1024,
    variables: [],
    tags: [],
  })
  const [schemaText, setSchemaText] = useState("")

  const loadPrompts = useCallback(async () => {
    try {
      const res = await api.listPrompts()
      setPrompts(res.data)
    } catch {
      /* ignore */
    }
  }, [])

  useEffect(() => {
    loadPrompts()
    api.models().then((r) => setModels(r.data.filter((m) => m.status === "active"))).catch(() => {})
  }, [loadPrompts])

  function selectPrompt(p: Prompt) {
    setSelected(p)
    setForm({
      name: p.name,
      user_prompt_template: p.user_prompt_template,
      description: p.description,
      system_prompt: p.system_prompt,
      model: p.model,
      agent_type: p.agent_type,
      output_json_schema: p.output_json_schema,
      temperature: p.temperature,
      max_tokens: p.max_tokens,
      variables: p.variables,
      tags: p.tags,
    })
    setSchemaText(p.output_json_schema ? JSON.stringify(p.output_json_schema, null, 2) : "")
  }

  function newPrompt() {
    setSelected(null)
    setForm({
      name: "",
      user_prompt_template: "",
      description: "",
      system_prompt: "",
      model: "",
      agent_type: "analysis",
      output_json_schema: null,
      temperature: 0.7,
      max_tokens: 1024,
      variables: [],
      tags: [],
    })
    setSchemaText("")
  }

  function updateTemplate(val: string) {
    const vars = [...val.matchAll(/\{\{(\w+)\}\}/g)].map((m) => m[1])
    setForm((f) => ({
      ...f,
      user_prompt_template: val,
      variables: [...new Set(vars)],
    }))
  }

  async function handleSave() {
    setSaving(true)
    try {
      let schema: Record<string, unknown> | null = null
      if (schemaText.trim()) {
        try {
          schema = JSON.parse(schemaText)
        } catch {
          alert("Invalid JSON schema")
          setSaving(false)
          return
        }
      }
      const body = { ...form, output_json_schema: schema }

      if (selected) {
        await api.updatePrompt(selected.id, body)
      } else {
        const res = await api.createPrompt(body)
        setSelected(res.data)
      }
      await loadPrompts()
    } catch {
      alert("Save failed")
    }
    setSaving(false)
  }

  async function handleDelete() {
    if (!selected) return
    if (!confirm("Delete this prompt?")) return
    await api.deletePrompt(selected.id)
    newPrompt()
    await loadPrompts()
  }

  async function handleDuplicate() {
    if (!selected) return
    const body: PromptCreate = {
      ...form,
      name: form.name + " (copy)",
    }
    const res = await api.createPrompt(body)
    setSelected(res.data)
    await loadPrompts()
  }

  function addTag() {
    if (!tagInput.trim()) return
    setForm((f) => ({
      ...f,
      tags: [...new Set([...f.tags!, tagInput.trim()])],
    }))
    setTagInput("")
  }

  function removeTag(tag: string) {
    setForm((f) => ({ ...f, tags: f.tags!.filter((t) => t !== tag) }))
  }

  return (
    <div className="grid grid-cols-[300px_1fr] gap-5 h-[calc(100vh-8rem)]">
      {/* Left: Prompt List */}
      <Card className="glass overflow-hidden flex flex-col">
        <CardHeader className="pb-3 flex flex-row items-center justify-between shrink-0">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <FileText className="h-4 w-4 text-purple-400" />
            Prompts
          </CardTitle>
          <Button size="sm" variant="ghost" onClick={newPrompt} className="h-8 w-8 p-0">
            <Plus className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="p-2 overflow-y-auto scrollbar-thin flex-1">
          {prompts.map((p) => (
            <button
              key={p.id}
              onClick={() => selectPrompt(p)}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-sm mb-1 transition-all duration-200 ${
                selected?.id === p.id
                  ? "bg-primary/15 text-foreground border border-primary/20"
                  : "hover:bg-white/[0.04] text-muted-foreground border border-transparent"
              }`}
            >
              <div className="font-medium truncate">{p.name}</div>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-[11px] text-muted-foreground">v{p.version}</span>
                <span className="text-[11px] text-muted-foreground/40">|</span>
                <span className="text-[11px] text-muted-foreground">{p.agent_type}</span>
              </div>
            </button>
          ))}
          {prompts.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="h-10 w-10 rounded-lg bg-muted/30 flex items-center justify-center mb-3">
                <FileText className="h-5 w-5 text-muted-foreground/40" />
              </div>
              <p className="text-xs text-muted-foreground">No prompts yet</p>
              <p className="text-[11px] text-muted-foreground/60 mt-0.5">
                Click + to create one
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Right: Editor Form */}
      <Card className="glass overflow-y-auto scrollbar-thin">
        <CardHeader className="flex flex-row items-center justify-between pb-3 sticky top-0 z-10 bg-card/90 backdrop-blur-sm border-b border-white/[0.04]">
          <CardTitle className="text-sm font-medium">
            {selected ? `Edit: ${selected.name}` : "New Prompt"}
            {selected && (
              <Badge variant="outline" className="ml-2 text-[11px]">v{selected.version}</Badge>
            )}
          </CardTitle>
          <div className="flex gap-2">
            {selected && (
              <>
                <Button size="sm" variant="ghost" onClick={handleDuplicate} className="h-8 text-xs gap-1.5">
                  <Copy className="h-3.5 w-3.5" /> Duplicate
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-8 text-xs text-red-400 gap-1.5 hover:text-red-300 hover:bg-red-500/10"
                  onClick={handleDelete}
                >
                  <Trash2 className="h-3.5 w-3.5" /> Delete
                </Button>
              </>
            )}
            <Button size="sm" onClick={handleSave} disabled={saving || !form.name} className="h-8 text-xs gap-1.5">
              {saving ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Save className="h-3.5 w-3.5" />
              )}
              Save
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-5 p-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label className="text-xs">Name</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="my-analysis-prompt"
                className="bg-muted/30 border-white/[0.06]"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs">Agent Type</Label>
              <select
                value={form.agent_type}
                onChange={(e) =>
                  setForm((f) => ({ ...f, agent_type: e.target.value }))
                }
                className="select-styled"
              >
                <option value="analysis">Analysis</option>
                <option value="summarization">Summarization</option>
                <option value="recommendation">Recommendation</option>
              </select>
            </div>
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">Description</Label>
            <Textarea
              value={form.description}
              onChange={(e) =>
                setForm((f) => ({ ...f, description: e.target.value }))
              }
              placeholder="What does this prompt do?"
              rows={2}
              className="bg-muted/30 border-white/[0.06] resize-none"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">System Prompt</Label>
            <Textarea
              value={form.system_prompt}
              onChange={(e) =>
                setForm((f) => ({ ...f, system_prompt: e.target.value }))
              }
              placeholder="You are a helpful assistant..."
              rows={3}
              className="font-mono text-xs bg-muted/30 border-white/[0.06] resize-none"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">
              User Prompt Template{" "}
              <span className="text-muted-foreground/60 font-normal">
                (use {"{{variable}}"} for placeholders)
              </span>
            </Label>
            <Textarea
              value={form.user_prompt_template}
              onChange={(e) => updateTemplate(e.target.value)}
              placeholder="Analyze the following data: {{input}}"
              rows={5}
              className="font-mono text-xs bg-muted/30 border-white/[0.06] resize-none"
            />
            {form.variables && form.variables.length > 0 && (
              <div className="flex items-center gap-1.5 flex-wrap mt-1.5">
                <span className="text-[11px] text-muted-foreground">Variables:</span>
                {form.variables.map((v) => (
                  <Badge key={v} variant="secondary" className="text-[11px] font-mono">
                    {`{{${v}}}`}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <Label className="text-xs">Model</Label>
              <select
                value={form.model}
                onChange={(e) =>
                  setForm((f) => ({ ...f, model: e.target.value }))
                }
                className="select-styled"
              >
                <option value="">Default</option>
                {models.map((m) => (
                  <option key={m.model} value={m.model}>
                    {m.model}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs">Temperature</Label>
              <Input
                type="number"
                min={0}
                max={2}
                step={0.1}
                value={form.temperature}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    temperature: parseFloat(e.target.value) || 0,
                  }))
                }
                className="bg-muted/30 border-white/[0.06] font-mono"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs">Max Tokens</Label>
              <Input
                type="number"
                min={1}
                value={form.max_tokens}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    max_tokens: parseInt(e.target.value) || 1024,
                  }))
                }
                className="bg-muted/30 border-white/[0.06] font-mono"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">Output JSON Schema <span className="text-muted-foreground/60 font-normal">(optional)</span></Label>
            <Textarea
              value={schemaText}
              onChange={(e) => setSchemaText(e.target.value)}
              placeholder='{"type": "object", "properties": {...}}'
              rows={4}
              className="font-mono text-xs bg-muted/30 border-white/[0.06] resize-none"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">Tags</Label>
            <div className="flex gap-2">
              <Input
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addTag())}
                placeholder="Add tag..."
                className="flex-1 bg-muted/30 border-white/[0.06]"
              />
              <Button size="sm" variant="secondary" onClick={addTag} className="h-9">
                Add
              </Button>
            </div>
            {form.tags && form.tags.length > 0 && (
              <div className="flex gap-1.5 flex-wrap mt-1.5">
                {form.tags.map((t) => (
                  <Badge
                    key={t}
                    variant="secondary"
                    className="text-[11px] gap-1 pl-2 cursor-pointer hover:bg-destructive/20 transition-colors"
                    onClick={() => removeTag(t)}
                  >
                    {t}
                    <X className="h-3 w-3" />
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
