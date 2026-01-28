import { useState, useEffect } from 'react'
import axios from 'axios'

interface Stats {
  total_messages: number
  toxic_messages: number
  clean_messages: number
  toxicity_rate: number
  intents: Record<string, number>
  tones: Record<string, number>
  active_connections: number
}

interface StatsPanelProps {
  apiUrl: string
}

export default function StatsPanel({ apiUrl }: StatsPanelProps) {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${apiUrl}/api/stats`)
      setStats(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          📈 Statistics
        </h3>
        <p className="text-gray-500 text-sm">Loading...</p>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          📈 Statistics
        </h3>
        <p className="text-gray-500 text-sm">Unable to load statistics</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        📈 Statistics
      </h3>

      {/* Active Users */}
      <div className="mb-4 p-3 bg-green-50 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-700">Active Users</span>
          <span className="text-xl font-bold text-green-600">
            {stats.active_connections}
          </span>
        </div>
      </div>

      {/* Total Messages */}
      <div className="mb-4 p-3 bg-blue-50 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-700">Total Messages</span>
          <span className="text-xl font-bold text-blue-600">
            {stats.total_messages}
          </span>
        </div>
      </div>

      {/* Toxicity Rate */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Toxicity Rate</span>
          <span className="text-sm font-bold text-red-600">
            {stats.toxicity_rate.toFixed(1)}%
          </span>
        </div>
        <div className="flex gap-2 text-xs">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded mr-1"></div>
            <span>Clean: {stats.clean_messages}</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded mr-1"></div>
            <span>Toxic: {stats.toxic_messages}</span>
          </div>
        </div>
      </div>

      {/* Intent Breakdown */}
      {Object.keys(stats.intents).length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Intent Breakdown</h4>
          <div className="space-y-2">
            {Object.entries(stats.intents)
              .sort(([, a], [, b]) => (b as number) - (a as number))
              .slice(0, 5)
              .map(([intent, count]) => (
                <div key={intent} className="flex justify-between text-xs">
                  <span className="capitalize text-gray-600">{intent}</span>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Tone Breakdown */}
      {Object.keys(stats.tones).length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Tone Breakdown</h4>
          <div className="space-y-2">
            {Object.entries(stats.tones)
              .sort(([, a], [, b]) => (b as number) - (a as number))
              .slice(0, 5)
              .map(([tone, count]) => (
                <div key={tone} className="flex justify-between text-xs">
                  <span className="capitalize text-gray-600">{tone}</span>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
          </div>
        </div>
      )}

      <p className="text-xs text-gray-500 mt-4 text-center">
        Updates every 5 seconds
      </p>
    </div>
  )
}
