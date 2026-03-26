import { useState, useRef, useEffect } from "react"
import { api, type ChatResponse, type DataSourceInfo, type DataSourceRef, type ModelInfo } from "../api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Loader2, MessageSquare, Send, X, Bot, User } from "lucide-react"

interface ChatMessage {
  role: "user" | "assistant"
  content: string
  data_sources_used?: { id: string; name: string }[]
  confidence?: number
  steps?: string[]
  model?: string
}

interface ChatPanelProps {
  dataSources: DataSourceInfo[]
  models: ModelInfo[]
  selectedModel: string
}

export function ChatPanel({ dataSources, models, selectedModel }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [agentType, setAgentType] = useState("analysis")
  const [chatModel, setChatModel] = useState(selectedModel)

  const [showMentions, setShowMentions] = useState(false)
  const [mentionFilter, setMentionFilter] = useState("")
  const [selectedSources, setSelectedSources] = useState<DataSourceRef[]>([])
  const [mentionIndex, setMentionIndex] = useState(0)

  const inputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  useEffect(() => {
    setChatModel(selectedModel)
  }, [selectedModel])

  const activeModels = models.filter((m) => m.status === "active")
  const modelsByProvider: Record<string, ModelInfo[]> = {}
  for (const m of activeModels) {
    if (!modelsByProvider[m.provider]) modelsByProvider[m.provider] = []
    modelsByProvider[m.provider].push(m)
  }

  const filteredSources = dataSources.filter(
    (ds) =>
      ds.name.toLowerCase().includes(mentionFilter.toLowerCase()) &&
      !selectedSources.some((s) => s.data_source_id === ds.id)
  )

  function handleInputChange(value: string) {
    setInput(value)
    const atIndex = value.lastIndexOf("@")
    if (atIndex !== -1) {
      const afterAt = value.slice(atIndex + 1)
      if (!afterAt.includes(" ")) {
        setShowMentions(true)
        setMentionFilter(afterAt)
        setMentionIndex(0)
        return
      }
    }
    setShowMentions(false)
    setMentionFilter("")
  }

  function selectMention(ds: DataSourceInfo) {
    setSelectedSources((prev) => [
      ...prev,
      { data_source_id: ds.id, data_source_name: ds.name },
    ])
    const atIndex = input.lastIndexOf("@")
    setInput(atIndex > 0 ? input.slice(0, atIndex) : "")
    setShowMentions(false)
    setMentionFilter("")
    inputRef.current?.focus()
  }

  function removeMention(sourceId: string) {
    setSelectedSources((prev) =>
      prev.filter((s) => s.data_source_id !== sourceId)
    )
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (showMentions && filteredSources.length > 0) {
      if (e.key === "ArrowDown") {
        e.preventDefault()
        setMentionIndex((i) => Math.min(i + 1, filteredSources.length - 1))
        return
      }
      if (e.key === "ArrowUp") {
        e.preventDefault()
        setMentionIndex((i) => Math.max(i - 1, 0))
        return
      }
      if (e.key === "Enter" || e.key === "Tab") {
        e.preventDefault()
        selectMention(filteredSources[mentionIndex])
        return
      }
      if (e.key === "Escape") {
        setShowMentions(false)
        return
      }
    }
    if (e.key === "Enter" && !showMentions) {
      e.preventDefault()
      handleSend()
    }
  }

  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return

    const userMessage: ChatMessage = {
      role: "user",
      content: text,
      data_sources_used: selectedSources.map((s) => ({
        id: s.data_source_id,
        name: s.data_source_name,
      })),
    }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setError("")
    setLoading(true)

    try {
      const req = {
        message: text,
        data_sources: selectedSources,
        agent_type: agentType,
        ...(chatModel ? { model: chatModel } : {}),
      }
      const res = await api.chat(req)
      const data: ChatResponse = res.data
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          data_sources_used: data.data_sources_used,
          confidence: data.confidence,
          steps: data.steps,
          model: data.model,
        },
      ])
      setSelectedSources([])
    } catch {
      setError("Chat request failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="glass">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-cyan-400" />
          Chat
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Messages */}
        <div className="h-[360px] overflow-y-auto scrollbar-thin rounded-xl border border-white/[0.04] bg-muted/10 p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="h-12 w-12 rounded-xl bg-muted/30 flex items-center justify-center mb-3">
                <MessageSquare className="h-6 w-6 text-muted-foreground/40" />
              </div>
              <p className="text-sm text-muted-foreground">
                Start a conversation
              </p>
              <p className="text-xs text-muted-foreground/60 mt-1">
                Use <kbd className="px-1.5 py-0.5 rounded bg-muted/50 text-[11px] font-mono">@</kbd> to reference data sources
              </p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
            >
              <div className={`h-7 w-7 rounded-lg flex items-center justify-center shrink-0 ${
                msg.role === "user"
                  ? "bg-primary/20"
                  : "bg-cyan-500/15"
              }`}>
                {msg.role === "user" ? (
                  <User className="h-3.5 w-3.5 text-primary" />
                ) : (
                  <Bot className="h-3.5 w-3.5 text-cyan-400" />
                )}
              </div>
              <div
                className={`max-w-[75%] rounded-xl px-4 py-2.5 text-sm ${
                  msg.role === "user"
                    ? "bg-primary/15 text-foreground"
                    : "bg-white/[0.04] text-foreground"
                }`}
              >
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                {msg.role === "user" && msg.data_sources_used && msg.data_sources_used.length > 0 && (
                  <div className="flex gap-1 mt-2 flex-wrap">
                    {msg.data_sources_used.map((ds) => (
                      <Badge key={ds.id} variant="outline" className="text-[11px]">
                        @{ds.name}
                      </Badge>
                    ))}
                  </div>
                )}
                {msg.role === "assistant" && (
                  <div className="mt-2 pt-2 border-t border-white/[0.06] space-y-1">
                    {msg.data_sources_used && msg.data_sources_used.length > 0 && (
                      <div className="flex gap-1 flex-wrap">
                        <span className="text-[11px] text-muted-foreground">Sources:</span>
                        {msg.data_sources_used.map((ds) => (
                          <Badge key={ds.id} variant="outline" className="text-[11px]">
                            {ds.name}
                          </Badge>
                        ))}
                      </div>
                    )}
                    {msg.confidence !== undefined && (
                      <p className="text-[11px] text-muted-foreground">
                        Confidence: <span className="text-emerald-400 font-mono">{(msg.confidence * 100).toFixed(1)}%</span>
                        {msg.model && (
                          <> | Model: <span className="font-mono">{msg.model}</span></>
                        )}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="h-7 w-7 rounded-lg bg-cyan-500/15 flex items-center justify-center shrink-0">
                <Bot className="h-3.5 w-3.5 text-cyan-400" />
              </div>
              <div className="rounded-xl bg-white/[0.04] px-4 py-3">
                <div className="flex gap-1.5">
                  <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce [animation-delay:0ms]" />
                  <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce [animation-delay:150ms]" />
                  <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce [animation-delay:300ms]" />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <p className="text-xs text-red-400">{error}</p>
        )}

        {/* Selected data sources chips */}
        {selectedSources.length > 0 && (
          <div className="flex gap-1.5 flex-wrap">
            {selectedSources.map((s) => (
              <Badge
                key={s.data_source_id}
                variant="secondary"
                className="text-xs gap-1 pl-2"
              >
                @{s.data_source_name}
                <button
                  onClick={() => removeMention(s.data_source_id)}
                  className="ml-0.5 hover:text-red-400 transition-colors"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}

        {/* Input area */}
        <div className="relative">
          {showMentions && filteredSources.length > 0 && (
            <div className="absolute bottom-full mb-1.5 left-0 w-72 max-h-40 overflow-y-auto scrollbar-thin rounded-lg border border-white/[0.08] bg-popover shadow-2xl z-10">
              {filteredSources.map((ds, i) => (
                <button
                  key={ds.id}
                  onClick={() => selectMention(ds)}
                  className={`w-full text-left px-3 py-2.5 text-sm transition-colors ${
                    i === mentionIndex ? "bg-primary/10 text-foreground" : "hover:bg-muted/50"
                  }`}
                >
                  <span className="font-medium">{ds.name}</span>
                  <span className="text-[11px] text-muted-foreground ml-2">
                    {ds.source_type} ({ds.record_count} records)
                  </span>
                </button>
              ))}
            </div>
          )}
          <div className="flex gap-2">
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => handleInputChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message... Use @ to mention data sources"
              className="flex-1 h-10 rounded-lg border border-input bg-muted/30 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring/40 focus:border-primary/50 transition-colors placeholder:text-muted-foreground/50"
              disabled={loading}
            />
            <select
              value={agentType}
              onChange={(e) => setAgentType(e.target.value)}
              className="select-styled w-[140px]"
            >
              <option value="analysis">Analysis</option>
              <option value="summarization">Summarization</option>
              <option value="recommendation">Recommendation</option>
            </select>
            <select
              value={chatModel}
              onChange={(e) => setChatModel(e.target.value)}
              className="select-styled w-[160px]"
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
            <Button onClick={handleSend} disabled={loading || !input.trim()} size="icon" className="h-10 w-10 shrink-0">
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
