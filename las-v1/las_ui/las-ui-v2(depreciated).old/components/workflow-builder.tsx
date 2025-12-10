"use client"

import { useCallback, useState } from 'react'
import {
    ReactFlow,
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    addEdge,
    Node,
    Edge,
    Connection,
    BackgroundVariant,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Save, Play } from 'lucide-react'
import { lasApi } from '@/lib/api'

const initialNodes: Node[] = [
    {
        id: '1',
        type: 'input',
        data: { label: 'Start' },
        position: { x: 250, y: 5 },
    },
]

const initialEdges: Edge[] = []

export function WorkflowBuilder() {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
    const [workflowName, setWorkflowName] = useState('Untitled Workflow')
    const [isSaving, setIsSaving] = useState(false)

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge(params, eds)),
        [setEdges]
    )

    const saveWorkflow = async () => {
        setIsSaving(true)
        try {
            const workflow = {
                name: workflowName,
                nodes: nodes.map(node => ({
                    id: node.id,
                    type: node.type || 'default',
                    position: node.position,
                    data: node.data,
                })),
                edges: edges.map(edge => ({
                    id: edge.id,
                    source: edge.source,
                    target: edge.target,
                    label: edge.label,
                })),
            }

            const response = await lasApi.saveWorkflow(workflow)

            if (response) {
                alert('Workflow saved successfully!')
            }
        } catch (error) {
            console.error('Failed to save workflow:', error)
            alert('Failed to save workflow')
        } finally {
            setIsSaving(false)
        }
    }

    const addAgentNode = () => {
        const newNode: Node = {
            id: `agent-${Date.now()}`,
            type: 'default',
            data: { label: 'Agent' },
            position: { x: Math.random() * 400, y: Math.random() * 400 },
        }
        setNodes((nds) => nds.concat(newNode))
    }

    const addToolNode = () => {
        const newNode: Node = {
            id: `tool-${Date.now()}`,
            type: 'default',
            data: { label: 'Tool' },
            position: { x: Math.random() * 400, y: Math.random() * 400 },
        }
        setNodes((nds) => nds.concat(newNode))
    }

    return (
        <div className="h-screen flex flex-col">
            {/* Toolbar */}
            <div className="border-b p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Input
                        type="text"
                        value={workflowName}
                        onChange={(e) => setWorkflowName(e.target.value)}
                        className="text-xl font-semibold max-w-md"
                        placeholder="Workflow Name"
                    />
                </div>
                <div className="flex gap-2">
                    <Button onClick={addAgentNode} variant="outline">
                        Add Agent
                    </Button>
                    <Button onClick={addToolNode} variant="outline">
                        Add Tool
                    </Button>
                    <Button onClick={saveWorkflow} disabled={isSaving}>
                        <Save className="mr-2 h-4 w-4" />
                        {isSaving ? 'Saving...' : 'Save'}
                    </Button>
                    <Button>
                        <Play className="mr-2 h-4 w-4" />
                        Run
                    </Button>
                </div>
            </div>

            {/* Canvas */}
            <div className="flex-1">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                >
                    <Controls />
                    <MiniMap />
                    <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
                </ReactFlow>
            </div>
        </div>
    )
}
