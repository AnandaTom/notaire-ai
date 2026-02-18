/**
 * Badge d'affichage pour la détection du viager
 * Affiche le type détecté, la confiance et les marqueurs
 */

import { DetectionResult } from '@/lib/api/promesse';

interface ViagerBadgeProps {
  detection: DetectionResult;
  className?: string;
}

export default function ViagerBadge({ detection, className = '' }: ViagerBadgeProps) {
  const { sous_type, confiance, marqueurs_detectes, avertissement } = detection;

  if (!sous_type) return null;

  type BadgeColor = 'blue' | 'yellow' | 'green' | 'purple' | 'gray';

  interface BadgeConfig {
    color: BadgeColor;
    icon: string;
    label: string;
    description: string;
  }

  // Couleurs et icones par sous-type
  const typeConfig: Record<string, BadgeConfig> = {
    viager: {
      color: 'blue',
      icon: '🏡',
      label: 'Viager Détecté',
      description: 'Promesse de vente en viager',
    },
    creation: {
      color: 'yellow',
      icon: '🏗️',
      label: 'Création Copropriété',
      description: 'Copropriété en cours de création',
    },
    lotissement: {
      color: 'green',
      icon: '🏘️',
      label: 'Lotissement',
      description: 'Bien dans un lotissement',
    },
    groupe_habitations: {
      color: 'purple',
      icon: '🏠',
      label: 'Groupe d\'Habitations',
      description: 'Bien dans un groupe d\'habitations',
    },
  };

  const config: BadgeConfig = typeConfig[sous_type] || {
    color: 'gray',
    icon: '📄',
    label: sous_type,
    description: 'Type spécifique détecté',
  };

  const colorClasses: Record<BadgeColor, string> = {
    blue: 'bg-blue-50 border-blue-200 text-blue-900',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    green: 'bg-green-50 border-green-200 text-green-900',
    purple: 'bg-purple-50 border-purple-200 text-purple-900',
    gray: 'bg-gray-50 border-gray-200 text-gray-900',
  };

  const textColorClasses: Record<BadgeColor, string> = {
    blue: 'text-blue-700',
    yellow: 'text-yellow-700',
    green: 'text-green-700',
    purple: 'text-purple-700',
    gray: 'text-gray-700',
  };

  return (
    <div className={`rounded-lg border-2 p-4 mb-4 ${colorClasses[config.color]} ${className}`}>
      <div className="flex items-start gap-3">
        <span className="text-3xl" role="img" aria-label={config.label}>
          {config.icon}
        </span>

        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-lg">{config.label}</h3>
            <span className={`text-sm font-medium ${textColorClasses[config.color]}`}>
              Confiance: {Math.round(confiance)}%
            </span>
          </div>

          <p className={`text-sm mb-2 ${textColorClasses[config.color]}`}>
            {config.description}
          </p>

          {sous_type === 'viager' && (
            <div className="flex flex-wrap gap-2 mt-3">
              <span className="inline-flex items-center gap-1 text-xs bg-white px-2 py-1 rounded border border-blue-300">
                💰 Bouquet + Rente
              </span>
              <span className="inline-flex items-center gap-1 text-xs bg-white px-2 py-1 rounded border border-blue-300">
                🏡 DUH (Droit d'Usage et d'Habitation)
              </span>
              <span className="inline-flex items-center gap-1 text-xs bg-white px-2 py-1 rounded border border-blue-300">
                📋 Certificat Médical
              </span>
              <span className="inline-flex items-center gap-1 text-xs bg-white px-2 py-1 rounded border border-blue-300">
                🔒 Privilège Vendeur
              </span>
            </div>
          )}

          {avertissement && (
            <div className="mt-3 p-2 bg-white rounded border border-yellow-400 text-sm text-yellow-800">
              ⚠️ {avertissement}
            </div>
          )}

          {/* Détails techniques (repliable) */}
          <details className="mt-3">
            <summary className={`text-xs cursor-pointer ${textColorClasses[config.color]} hover:underline`}>
              Détails de détection ({marqueurs_detectes.length} marqueurs)
            </summary>
            <div className="mt-2 p-2 bg-white rounded text-xs">
              <ul className="list-disc list-inside space-y-1">
                {marqueurs_detectes.map((marqueur, idx) => (
                  <li key={idx} className="text-gray-700">
                    {marqueur.replace(/_/g, ' ')}
                  </li>
                ))}
              </ul>
            </div>
          </details>
        </div>
      </div>
    </div>
  );
}
