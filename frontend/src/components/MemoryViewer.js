import React from 'react';

function MemoryViewer({ memories, type }) {
  if (memories.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
        <p className="text-gray-400">Nenhuma memória {type.toUpperCase()} encontrada.</p>
      </div>
    );
  }

  const getTypeColor = () => {
    switch (type) {
      case 'hot':
        return 'border-blue-500';
      case 'cold':
        return 'border-purple-500';
      case 'archive':
        return 'border-gray-500';
      default:
        return 'border-gray-700';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-PT');
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {memories.map((memory) => (
        <div
          key={memory.id}
          className={`memory-card bg-gray-800 rounded-lg p-4 border-l-4 ${getTypeColor()} border border-gray-700`}
          data-testid={`memory-card-${memory.id}`}
        >
          <div className="flex items-start justify-between mb-2">
            <h3 className="font-semibold text-white">{memory.key}</h3>
            <span className="text-xs text-gray-500">
              {type === 'hot' ? '💡' : type === 'cold' ? '❄️' : '🗄️'}
            </span>
          </div>

          <div className="text-sm text-gray-300 mb-3">
            {typeof memory.value === 'string'
              ? memory.value
              : JSON.stringify(memory.value, null, 2)}
          </div>

          {memory.tags && memory.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {memory.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          <div className="text-xs text-gray-500 mt-2">
            {type === 'hot' && memory.expires_at && (
              <div>Expira: {formatDate(memory.expires_at)}</div>
            )}
            {type === 'archive' && memory.archived_reason && (
              <div>Razão: {memory.archived_reason}</div>
            )}
            <div>Criado: {formatDate(memory.created_at)}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default MemoryViewer;
