import React from 'react';

function ApprovalDialog({ action, onApprove, onReject }) {
  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
      data-testid="approval-dialog"
    >
      <div className="bg-gray-800 rounded-lg p-8 max-w-2xl w-full mx-4 border border-gray-700">
        <h2 className="text-2xl font-bold text-yellow-400 mb-4">
          ⚠️ Aprovação Necessária
        </h2>

        <div className="mb-6">
          <div className="mb-4">
            <div className="text-sm text-gray-400 mb-2">Ação:</div>
            <div className="text-lg text-white font-semibold">{action.action_type}</div>
          </div>

          <div>
            <div className="text-sm text-gray-400 mb-2">Dados:</div>
            <pre className="bg-gray-900 text-gray-300 p-4 rounded text-xs overflow-x-auto">
              {JSON.stringify(action.payload, null, 2)}
            </pre>
          </div>
        </div>

        <div className="bg-yellow-900 border border-yellow-700 rounded-lg p-4 mb-6">
          <p className="text-yellow-200 text-sm">
            <strong>⚠️ Atenção:</strong> Esta ação será executada no sistema. Certifique-se
            de que compreende os efeitos antes de aprovar.
          </p>
        </div>

        <div className="flex space-x-4">
          <button
            onClick={onApprove}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white rounded-lg px-6 py-3 font-medium transition-colors"
            data-testid="approve-button"
          >
            ✅ Aprovar e Executar
          </button>
          <button
            onClick={onReject}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white rounded-lg px-6 py-3 font-medium transition-colors"
            data-testid="reject-button"
          >
            ❌ Rejeitar
          </button>
        </div>
      </div>
    </div>
  );
}

export default ApprovalDialog;
