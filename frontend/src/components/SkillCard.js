import React from 'react';

function SkillCard({ skill }) {
  return (
    <div
      className="memory-card bg-gray-800 rounded-lg p-6 border border-gray-700"
      data-testid={`skill-card-${skill.id}`}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-white text-lg">🛠️ {skill.name}</h3>
        <span
          className={`px-2 py-1 text-xs rounded ${
            skill.is_enabled
              ? 'bg-green-900 text-green-300'
              : 'bg-red-900 text-red-300'
          }`}
        >
          v{skill.version}
        </span>
      </div>

      <p className="text-sm text-gray-300 mb-4">{skill.description}</p>

      <div className="mb-4">
        <div className="text-xs text-gray-400 mb-1">Quando usar:</div>
        <p className="text-sm text-gray-300 italic">{skill.when_to_use}</p>
      </div>

      {skill.steps && skill.steps.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-gray-400 mb-2">Passos ({skill.steps.length}):</div>
          <div className="space-y-1">
            {skill.steps.slice(0, 3).map((step, idx) => (
              <div
                key={idx}
                className="text-xs text-gray-300 bg-gray-700 rounded px-2 py-1"
              >
                {step.order}. {step.description}
              </div>
            ))}
            {skill.steps.length > 3 && (
              <div className="text-xs text-gray-500">
                +{skill.steps.length - 3} passos adicionais
              </div>
            )}
          </div>
        </div>
      )}

      {skill.tags && skill.tags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {skill.tags.map((tag, idx) => (
            <span
              key={idx}
              className="px-2 py-1 bg-blue-900 text-blue-300 text-xs rounded"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default SkillCard;
