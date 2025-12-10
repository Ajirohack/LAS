"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, TrendingUp, Zap, DollarSign } from 'lucide-react'
import { useEffect, useState } from 'react'

interface DashboardStats {
    totalQueries: number
    cacheHitRate: number
    totalCost: number
    activeWorkers: number
}

export function DashboardWidgets() {
    const [stats, setStats] = useState<DashboardStats>({
        totalQueries: 0,
        cacheHitRate: 0,
        totalCost: 0,
        activeWorkers: 0,
    })

    useEffect(() => {
        // Fetch stats from various APIs
        Promise.all([
            fetch('/api/perf/cache/stats').then(r => r.json()).catch(() => ({})),
            fetch('/api/perf/cost/summary').then(r => r.json()).catch(() => ({})),
            fetch('/api/perf/workers/stats').then(r => r.json()).catch(() => ({})),
        ]).then(([cacheData, costData, workerData]) => {
            setStats({
                totalQueries: cacheData.total_queries || 0,
                cacheHitRate: cacheData.hit_rate || 0,
                totalCost: costData.total_cost || 0,
                activeWorkers: workerData.active_workers || 0,
            })
        })
    }, [])

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Queries</CardTitle>
                    <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{stats.totalQueries.toLocaleString()}</div>
                    <p className="text-xs text-muted-foreground">
                        Agent queries processed
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Cache Hit Rate</CardTitle>
                    <Zap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{(stats.cacheHitRate * 100).toFixed(1)}%</div>
                    <p className="text-xs text-muted-foreground">
                        Semantic cache efficiency
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">${stats.totalCost.toFixed(2)}</div>
                    <p className="text-xs text-muted-foreground">
                        LLM API costs
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Active Workers</CardTitle>
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{stats.activeWorkers}</div>
                    <p className="text-xs text-muted-foreground">
                        Distributed workers online
                    </p>
                </CardContent>
            </Card>
        </div>
    )
}
