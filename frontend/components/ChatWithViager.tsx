/**
 * Exemple d'intégration du viager dans un composant Chat
 * Combine détection automatique + questions conditionnelles + validation
 */

'use client';

import { useState } from 'react';
import { useViagerDetection } from '@/hooks/useViagerDetection';
import ViagerBadge from './ViagerBadge';

export default function ChatWithViager() {
  const [donnees, setDonnees] = useState<Record<string, any>>({});
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([
    {
      role: 'assistant',
      content: 'Bonjour ! Je vais vous aider à créer votre promesse de vente. Pour commencer, quel type de bien souhaitez-vous vendre ?',
    },
  ]);

  // Hook de détection viager
  const {
    detection,
    isDetecting,
    questionsViager,
    isLoadingQuestions,
    validation,
    checkViagerRequired,
    getViagerWarnings,
    isViager,
  } = useViagerDetection(donnees, {
    autoDetect: true,
    validateOnChange: true,
  });

  /**
   * Gère la soumission d'un message utilisateur
   */
  const handleSendMessage = async (message: string) => {
    // Ajouter message utilisateur
    setMessages((prev) => [...prev, { role: 'user', content: message }]);

    // Extraire les données du message (parsing NL)
    // TODO: Implémenter parsing NL ou utiliser endpoint /agent/execute
    const extractedData = parseMessage(message);
    setDonnees((prev) => ({ ...prev, ...extractedData }));

    // Générer réponse assistant
    const response = generateResponse(extractedData);
    setMessages((prev) => [...prev, { role: 'assistant', content: response }]);
  };

  /**
   * Parse simple pour extraire données du message
   * Dans une vraie implémentation, utiliser /agent/execute
   */
  const parseMessage = (message: string): Record<string, any> => {
    const data: Record<string, any> = {};

    // Exemples de patterns simples
    if (/maison|appartement|terrain/i.test(message)) {
      data.bien = { nature: message.match(/maison|appartement|terrain/i)?.[0] };
    }

    if (/viager/i.test(message)) {
      data.prix = { ...donnees.prix, type_vente: 'viager' };
    }

    if (/(\d+)\s*(€|euros?)/i.test(message)) {
      const montant = parseInt(message.match(/(\d+)\s*(€|euros?)/i)?.[1] || '0');
      if (isViager && message.toLowerCase().includes('bouquet')) {
        data.prix = { ...donnees.prix, bouquet: { montant } };
      } else if (isViager && message.toLowerCase().includes('rente')) {
        data.prix = { ...donnees.prix, rente_viagere: { montant } };
      } else {
        data.prix = { ...donnees.prix, montant };
      }
    }

    return data;
  };

  /**
   * Génère une réponse contextuelle
   */
  const generateResponse = (extractedData: Record<string, any>): string => {
    // Si viager détecté, poser questions spécifiques
    if (isViager && questionsViager.length > 0) {
      const nextQuestion = questionsViager[0]?.questions.find(
        (q) => !donnees[q.variable]
      );
      if (nextQuestion) {
        return nextQuestion.texte;
      }
    }

    // Réponse générique
    return 'Merci pour cette information. Pouvez-vous me donner plus de détails ?';
  };

  /**
   * Affiche les champs viager requis manquants
   */
  const renderViagerRequired = () => {
    if (!isViager) return null;

    const { valid, missing } = checkViagerRequired();
    if (valid) return null;

    return (
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 mb-4">
        <h4 className="font-semibold text-orange-900 mb-2">
          ⚠️ Champs obligatoires manquants
        </h4>
        <ul className="list-disc list-inside text-sm text-orange-800 space-y-1">
          {missing.map((field, idx) => (
            <li key={idx}>{field}</li>
          ))}
        </ul>
      </div>
    );
  };

  /**
   * Affiche les warnings viager
   */
  const renderViagerWarnings = () => {
    if (!isViager) return null;

    const warnings = getViagerWarnings();
    if (warnings.length === 0) return null;

    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
        <h4 className="font-semibold text-yellow-900 mb-2">💡 Recommandations</h4>
        <ul className="list-disc list-inside text-sm text-yellow-800 space-y-1">
          {warnings.map((warning, idx) => (
            <li key={idx}>{warning}</li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold mb-2">Assistant Promesse de Vente</h1>
        {isDetecting && (
          <div className="text-sm text-gray-600">
            🔍 Analyse en cours...
          </div>
        )}
      </div>

      {/* Badge Viager */}
      {detection && <ViagerBadge detection={detection} />}

      {/* Champs requis */}
      {renderViagerRequired()}

      {/* Warnings */}
      {renderViagerWarnings()}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-lg ${
              msg.role === 'user'
                ? 'bg-blue-100 ml-auto max-w-[80%]'
                : 'bg-gray-100 mr-auto max-w-[80%]'
            }`}
          >
            <p className="text-sm">{msg.content}</p>
          </div>
        ))}

        {/* Questions Viager Conditionnelles */}
        {isViager && questionsViager.length > 0 && (
          <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-3">
              🏡 Questions Spécifiques Viager
            </h3>
            <div className="space-y-3">
              {questionsViager[0]?.questions.slice(0, 3).map((q) => (
                <div key={q.id} className="bg-white p-3 rounded border border-blue-200">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {q.texte}
                    {q.obligatoire && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  {q.help && (
                    <p className="text-xs text-gray-500 mb-2">{q.help}</p>
                  )}
                  {q.type === 'number' && (
                    <input
                      type="number"
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                      placeholder={q.placeholder}
                      onChange={(e) =>
                        setDonnees((prev) => ({
                          ...prev,
                          [q.variable]: parseInt(e.target.value),
                        }))
                      }
                    />
                  )}
                  {q.type === 'boolean' && (
                    <div className="flex gap-4">
                      <label className="flex items-center gap-2">
                        <input
                          type="radio"
                          name={q.id}
                          value="true"
                          onChange={() =>
                            setDonnees((prev) => ({ ...prev, [q.variable]: true }))
                          }
                        />
                        Oui
                      </label>
                      <label className="flex items-center gap-2">
                        <input
                          type="radio"
                          name={q.id}
                          value="false"
                          onChange={() =>
                            setDonnees((prev) => ({ ...prev, [q.variable]: false }))
                          }
                        />
                        Non
                      </label>
                    </div>
                  )}
                  {q.type === 'select' && (
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                      onChange={(e) =>
                        setDonnees((prev) => ({ ...prev, [q.variable]: e.target.value }))
                      }
                    >
                      <option value="">-- Sélectionner --</option>
                      {q.options?.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {isLoadingQuestions && (
          <div className="text-center text-gray-600 text-sm">
            Chargement des questions viager...
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
          placeholder="Décrivez votre projet (ex: Je veux vendre ma maison en viager pour 150000€)"
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSendMessage(e.currentTarget.value);
              e.currentTarget.value = '';
            }
          }}
        />
        <button
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          onClick={(e) => {
            const input = e.currentTarget.previousElementSibling as HTMLInputElement;
            if (input.value) {
              handleSendMessage(input.value);
              input.value = '';
            }
          }}
        >
          Envoyer
        </button>
      </div>

      {/* Debug */}
      {process.env.NODE_ENV === 'development' && (
        <details className="mt-4 text-xs">
          <summary className="cursor-pointer text-gray-600">Debug: Données</summary>
          <pre className="mt-2 p-2 bg-gray-100 rounded overflow-auto max-h-40">
            {JSON.stringify(donnees, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}
