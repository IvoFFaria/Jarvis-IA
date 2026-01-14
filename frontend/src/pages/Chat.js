import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ApprovalDialog from '../components/ApprovalDialog';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const USER_ID = 'default_user';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [permissionLevel, setPermissionLevel] = useState('EXECUTE_APPROVED');
  const [pendingApproval, setPendingApproval] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, null, {
        params: {
          message: userMessage,
          user_id: USER_ID,
          permission_level: permissionLevel,
        },
      });

      const aiResponse = response.data.response;
      const skillsUsed = response.data.skills_used || [];
      const requiresApproval = response.data.requires_approval;
      const proposedAction = response.data.proposed_action;

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: aiResponse,
          skills_used: skillsUsed,
          requires_approval: requiresApproval,
        },
      ]);

      if (requiresApproval && proposedAction) {
        setPendingApproval(proposedAction);
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'error',
          content: 'Erro ao comunicar com o sistema. Por favor, tente novamente.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (approved) => {
    if (!pendingApproval) return;

    try {
      await axios.post(`${API}/approvals`, {
        user_id: USER_ID,
        action_type: pendingApproval.action_type,
        payload: pendingApproval.payload,
        approved: approved,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'system',
          content: approved
            ? `✅ Ação "${pendingApproval.action_type}" aprovada e executada.`
            : `❌ Ação "${pendingApproval.action_type}" rejeitada.`,
        },
      ]);
    } catch (error) {
      console.error('Erro ao registar aprovação:', error);
    } finally {
      setPendingApproval(null);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 flex flex-col h-screen" data-testid="chat-page">
      {/* Permission Level Selector */}
      <div className="mb-4 flex items-center justify-between bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div>
          <label className="text-gray-400 text-sm mr-4">Nível de Permissão:</label>
          <select
            value={permissionLevel}
            onChange={(e) => setPermissionLevel(e.target.value)}
            className="bg-gray-700 text-white rounded px-4 py-2 border border-gray-600 focus:outline-none focus:border-blue-400"
            data-testid="permission-selector"
          >
            <option value="READ_ONLY">🔒 READ_ONLY</option>
            <option value="DRAFT_ONLY">📋 DRAFT_ONLY</option>
            <option value="EXECUTE_APPROVED">✅ EXECUTE_APPROVED</option>
          </select>
        </div>
        <div className="text-sm text-gray-400">
          {permissionLevel === 'READ_ONLY' && '🔒 Apenas leitura'}
          {permissionLevel === 'DRAFT_ONLY' && '📋 Apenas propostas'}
          {permissionLevel === 'EXECUTE_APPROVED' && '✅ Executa com aprovação'}
        </div>
      </div>

      {/* Messages */}
      <div
        className="flex-1 bg-gray-800 rounded-lg p-6 overflow-y-auto mb-4 border border-gray-700"
        data-testid="chat-messages"
      >
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-20">
            <div className="text-6xl mb-4">🤖</div>
            <h2 className="text-2xl font-bold mb-2">Bem-vindo ao Jarvis</h2>
            <p className="text-sm">Como posso ajudá-lo hoje?</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`chat-message mb-4 ${
                msg.role === 'user' ? 'text-right' : 'text-left'
              }`}
            >
              <div
                className={`inline-block max-w-2xl rounded-lg px-6 py-4 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : msg.role === 'error'
                    ? 'bg-red-900 text-red-200'
                    : msg.role === 'system'
                    ? 'bg-gray-700 text-gray-200'
                    : 'bg-gray-700 text-white'
                }`}
                data-testid={`message-${idx}`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>

                {/* Skills Used */}
                {msg.skills_used && msg.skills_used.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-600">
                    <p className="text-xs text-gray-400 mb-1">Skills utilizadas:</p>
                    <div className="flex flex-wrap gap-2">
                      {msg.skills_used.map((skill, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 bg-green-900 text-green-300 text-xs rounded"
                        >
                          🛠️ {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Requires Approval Badge */}
                {msg.requires_approval && (
                  <div className="mt-3 pt-3 border-t border-gray-600">
                    <span className="px-2 py-1 bg-yellow-900 text-yellow-300 text-xs rounded">
                      ⚠️ Requer aprovação
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="text-left mb-4">
            <div className="inline-block bg-gray-700 rounded-lg px-6 py-4">
              <div className="flex items-center space-x-2">
                <div className="loading-spinner"></div>
                <span className="text-gray-400">Jarvis está pensando...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="flex space-x-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Digite sua mensagem..."
          className="flex-1 bg-gray-800 text-white rounded-lg px-6 py-4 border border-gray-700 focus:outline-none focus:border-blue-400"
          disabled={loading}
          data-testid="chat-input"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg px-8 py-4 font-medium transition-colors"
          data-testid="chat-send-button"
        >
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </form>

      {/* Approval Dialog */}
      {pendingApproval && (
        <ApprovalDialog
          action={pendingApproval}
          onApprove={() => handleApproval(true)}
          onReject={() => handleApproval(false)}
        />
      )}
    </div>
  );
}

export default Chat;
