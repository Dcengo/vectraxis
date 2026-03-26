import { useCallback, useRef } from "react"
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  type Connection,
  type Edge,
  type Node,
  type NodeTypes,
} from "@xyflow/react"
import "@xyflow/react/dist/style.css"

import { PromptNode } from "./nodes/PromptNode"
import { ConditionNode } from "./nodes/ConditionNode"
import { DataSourceNode } from "./nodes/DataSourceNode"
import { ValidatorNode } from "./nodes/ValidatorNode"
import { MergerNode } from "./nodes/MergerNode"
import { OutputNode } from "./nodes/OutputNode"

const nodeTypes: NodeTypes = {
  prompt: PromptNode,
  condition: ConditionNode,
  data_source: DataSourceNode,
  validator: ValidatorNode,
  merger: MergerNode,
  output: OutputNode,
}

interface WorkflowCanvasProps {
  initialNodes: Node[]
  initialEdges: Edge[]
  onNodesChange: (nodes: Node[]) => void
  onEdgesChange: (edges: Edge[]) => void
  onNodeSelect: (node: Node | null) => void
}

let nodeIdCounter = 0

export function WorkflowCanvas({
  initialNodes,
  initialEdges,
  onNodesChange: onNodesChangeCallback,
  onEdgesChange: onEdgesChangeCallback,
  onNodeSelect,
}: WorkflowCanvasProps) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const syncNodes = useCallback(
    (updatedNodes: Node[]) => {
      onNodesChangeCallback(updatedNodes)
    },
    [onNodesChangeCallback]
  )

  const syncEdges = useCallback(
    (updatedEdges: Edge[]) => {
      onEdgesChangeCallback(updatedEdges)
    },
    [onEdgesChangeCallback]
  )

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => {
        const newEdges = addEdge(
          { ...params, id: `e-${Date.now()}`, animated: true },
          eds
        )
        syncEdges(newEdges)
        return newEdges
      })
    },
    [setEdges, syncEdges]
  )

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = "move"
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const type = event.dataTransfer.getData("application/reactflow-type")
      const label = event.dataTransfer.getData("application/reactflow-label")

      if (!type || !reactFlowWrapper.current) return

      const bounds = reactFlowWrapper.current.getBoundingClientRect()
      const position = {
        x: event.clientX - bounds.left,
        y: event.clientY - bounds.top,
      }

      const newNode: Node = {
        id: `${type}-${++nodeIdCounter}-${Date.now()}`,
        type,
        position,
        data: { label, config: {} },
      }

      setNodes((nds) => {
        const updated = [...nds, newNode]
        syncNodes(updated)
        return updated
      })
    },
    [setNodes, syncNodes]
  )

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      onNodeSelect(node)
    },
    [onNodeSelect]
  )

  const onPaneClick = useCallback(() => {
    onNodeSelect(null)
  }, [onNodeSelect])

  const handleNodesChangeInternal = useCallback(
    (changes: Parameters<typeof onNodesChange>[0]) => {
      onNodesChange(changes)
      setTimeout(() => {
        setNodes((nds) => {
          syncNodes(nds)
          return nds
        })
      }, 0)
    },
    [onNodesChange, setNodes, syncNodes]
  )

  const handleEdgesChangeInternal = useCallback(
    (changes: Parameters<typeof onEdgesChange>[0]) => {
      onEdgesChange(changes)
      setTimeout(() => {
        setEdges((eds) => {
          syncEdges(eds)
          return eds
        })
      }, 0)
    },
    [onEdgesChange, setEdges, syncEdges]
  )

  return (
    <div ref={reactFlowWrapper} className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChangeInternal}
        onEdgesChange={handleEdgesChangeInternal}
        onConnect={onConnect}
        onDragOver={onDragOver}
        onDrop={onDrop}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        defaultEdgeOptions={{
          animated: true,
          style: { stroke: "hsl(258 80% 62%)", strokeWidth: 2 },
        }}
        style={{ background: "hsl(228 14% 6%)" }}
      >
        <Background color="hsl(228 14% 14%)" gap={20} size={1} />
        <Controls className="!bg-card !border-white/10 !rounded-lg !shadow-lg [&>button]:!bg-card [&>button]:!border-white/10 [&>button]:!text-foreground [&>button:hover]:!bg-muted" />
        <MiniMap
          className="!bg-card/80 !border-white/10 !rounded-lg"
          nodeColor={(n) => {
            switch (n.type) {
              case "prompt": return "rgb(168, 85, 247)"
              case "condition": return "rgb(234, 179, 8)"
              case "data_source": return "rgb(59, 130, 246)"
              case "validator": return "rgb(249, 115, 22)"
              case "merger": return "rgb(34, 211, 238)"
              case "output": return "rgb(52, 211, 153)"
              default: return "rgb(107, 114, 128)"
            }
          }}
          maskColor="rgba(0, 2, 22, 0.7)"
        />
      </ReactFlow>
    </div>
  )
}

export function updateNodeData(
  nodes: Node[],
  nodeId: string,
  updates: Partial<Record<string, unknown>>
): Node[] {
  return nodes.map((n) =>
    n.id === nodeId ? { ...n, data: { ...n.data, ...updates } } : n
  )
}
