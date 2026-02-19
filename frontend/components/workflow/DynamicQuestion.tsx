'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import type { Question, ValidationMessage } from '@/types/workflow'
import { TextField, NumberField, BooleanField, SelectField, DateField, ArrayField, ContactField } from './fields'
import { useWorkflowStore } from '@/stores/workflowStore'

interface DynamicQuestionProps {
  question: Question
  value: unknown
  onChange: (value: unknown) => void
  allValues?: Record<string, unknown>
}

export default function DynamicQuestion({ question, value, onChange, allValues }: DynamicQuestionProps) {
  const [fieldError, setFieldError] = useState<string | null>(null)
  const validateField = useWorkflowStore((s) => s.validateField)

  // Hooks AVANT tout return conditionnel (regle des hooks React)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!question.variable || value === undefined || value === '') {
      setFieldError(null)
      return
    }
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(async () => {
      const messages = await validateField(question.variable, value)
      const erreur = messages.find((m: ValidationMessage) => m.niveau === 'erreur')
      setFieldError(erreur?.message || null)
    }, 800)
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current) }
  }, [question.variable, value, validateField])

  const handleBlur = useCallback(async () => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    if (!question.variable || value === undefined || value === '') return
    const messages = await validateField(question.variable, value)
    const erreur = messages.find((m: ValidationMessage) => m.niveau === 'erreur')
    setFieldError(erreur?.message || null)
  }, [question.variable, value, validateField])

  // Evaluation condition d'affichage — APRES les hooks
  if (question.condition_affichage && allValues) {
    const visible = evaluateCondition(question.condition_affichage, allValues)
    if (!visible) return null
  }

  const renderField = () => {
    switch (question.type) {
      case 'texte':
      case 'texte_long':
        return (
          <TextField
            question={question}
            value={(value as string) || ''}
            onChange={onChange}
            onBlur={handleBlur}
            error={fieldError || undefined}
          />
        )

      case 'nombre':
        return (
          <NumberField
            question={question}
            value={(value as number | string) ?? ''}
            onChange={onChange}
            onBlur={handleBlur}
            error={fieldError || undefined}
          />
        )

      case 'booleen':
        return (
          <BooleanField
            question={question}
            value={value as boolean | null}
            onChange={onChange}
            error={fieldError || undefined}
          />
        )

      case 'choix':
        return (
          <SelectField
            question={question}
            value={(value as string) || ''}
            onChange={onChange}
            error={fieldError || undefined}
          />
        )

      case 'date':
        return (
          <DateField
            question={question}
            value={(value as string) || ''}
            onChange={onChange}
            onBlur={handleBlur}
            error={fieldError || undefined}
          />
        )

      case 'tableau':
        return (
          <ArrayField
            question={question}
            value={(value as string[]) || []}
            onChange={onChange}
            error={fieldError || undefined}
          />
        )

      case 'contact':
        return (
          <ContactField
            question={question}
            value={(value as Record<string, string>) || {}}
            onChange={onChange}
            onBlur={handleBlur}
            error={fieldError || undefined}
          />
        )

      default:
        return (
          <TextField
            question={question}
            value={(value as string) || ''}
            onChange={onChange}
            onBlur={handleBlur}
            error={fieldError || undefined}
          />
        )
    }
  }

  return (
    <div className="animate-fade-in">
      {renderField()}

      {/* Sous-questions recursives */}
      {question.sous_questions && question.sous_questions.length > 0 && Boolean(value) && (
        <div className="ml-4 mt-3 pl-4 border-l-2 border-champagne space-y-4">
          {question.sous_questions.map((sq) => (
            <DynamicQuestion
              key={sq.id}
              question={sq}
              value={getNestedValue(allValues ?? {}, sq.variable)}
              onChange={(v) => onChange(v)}
              allValues={allValues}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// Evalue une condition simple (ex: "situation_matrimoniale == marie")
function evaluateCondition(condition: string, values: Record<string, unknown>): boolean {
  try {
    // Format: "variable == valeur" ou "variable != valeur" ou "variable"
    if (condition.includes('==')) {
      const [path, expected] = condition.split('==').map((s) => s.trim().replace(/['"]/g, ''))
      return getNestedValue(values, path) === expected
    }
    if (condition.includes('!=')) {
      const [path, expected] = condition.split('!=').map((s) => s.trim().replace(/['"]/g, ''))
      return getNestedValue(values, path) !== expected
    }
    // Simple presence check
    const val = getNestedValue(values, condition.trim())
    return Boolean(val)
  } catch {
    return true // En cas de doute, afficher
  }
}

function getNestedValue(obj: Record<string, unknown>, path: string): unknown {
  return path.split('.').reduce((acc: unknown, key) => {
    if (acc && typeof acc === 'object') return (acc as Record<string, unknown>)[key]
    return undefined
  }, obj)
}
