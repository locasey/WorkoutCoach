import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Lock } from 'lucide-react'
import axios from 'axios'
import { useToast } from './Toast'
import './ModelSelector.css'

const PROVIDER_LABELS = {
  gemini: 'Google',
  anthropic: 'Anthropic',
  openai: 'OpenAI',
}

const PROVIDER_ORDER = ['gemini', 'anthropic', 'openai']

export default function ModelSelector({ currentPreferredModel }) {
  const queryClient = useQueryClient()
  const toast = useToast()
  const [tooltip, setTooltip] = useState(null) // model id with active tooltip

  const { data, isLoading } = useQuery({
    queryKey: ['llm-models'],
    queryFn: async () => {
      const res = await axios.get('/api/llm/models')
      return res.data
    },
  })

  const { mutate: selectModel, isPending } = useMutation({
    mutationFn: async (modelId) => {
      await axios.put('/api/user/preferences', { preferred_model: modelId })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] })
    },
    onError: (err) => {
      const message = err?.response?.data?.error || 'Failed to save model preference'
      toast.error(message)
    },
  })

  if (isLoading) {
    return <div className="model-selector__loading">Loading models…</div>
  }

  const models = data?.models || []
  const activeModelId = currentPreferredModel || data?.active_model

  // Group by provider in display order
  const grouped = PROVIDER_ORDER.reduce((acc, provider) => {
    const group = models.filter((m) => m.provider === provider)
    if (group.length > 0) acc.push({ provider, models: group })
    return acc
  }, [])

  return (
    <div className="model-selector">
      {grouped.map(({ provider, models: group }) => (
        <div key={provider} className="model-selector__group">
          <span className="model-selector__provider-label">
            {PROVIDER_LABELS[provider] || provider}
          </span>
          <div className="model-selector__pills">
            {group.map((model) => {
              const isActive = model.id === activeModelId
              const isLocked = !model.available
              const showTip = tooltip === model.id

              return (
                <div key={model.id} className="model-selector__pill-wrap">
                  <button
                    type="button"
                    disabled={isLocked || isPending}
                    aria-pressed={isActive}
                    className={[
                      'model-selector__pill',
                      isActive && 'model-selector__pill--active',
                      isLocked && 'model-selector__pill--locked',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                    onClick={() => !isLocked && selectModel(model.id)}
                    onMouseEnter={() => isLocked && setTooltip(model.id)}
                    onMouseLeave={() => setTooltip(null)}
                    onFocus={() => isLocked && setTooltip(model.id)}
                    onBlur={() => setTooltip(null)}
                    // Touch support for locked models
                    onTouchStart={() => isLocked && setTooltip(model.id)}
                    onTouchEnd={() => setTimeout(() => setTooltip(null), 1500)}
                  >
                    {isLocked && (
                      <Lock className="model-selector__lock-icon" size={11} aria-hidden />
                    )}
                    {model.label}
                  </button>
                  {isLocked && showTip && (
                    <div className="model-selector__tooltip" role="tooltip">
                      Available on Premium plan
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
