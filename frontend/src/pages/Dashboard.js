import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MemoryViewer from '../components/MemoryViewer';
import SkillCard from '../components/SkillCard';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const USER_ID = 'default_user';

function Dashboard() {
  const [hotMemories, setHotMemories] = useState([]);
  const [coldMemories, setColdMemories] = useState([]);
  const [archiveMemories, setArchiveMemories] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('hot');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [hotRes, coldRes, archiveRes, skillsRes] = await Promise.all([
        axios.get(`${API}/memory/hot?user_id=${USER_ID}`),
        axios.get(`${API}/memory/cold?user_id=${USER_ID}`),
        axios.get(`${API}/memory/archive?user_id=${USER_ID}`),
        axios.get(`${API}/skills?enabled_only=true&limit=10`),
      ]);

      setHotMemories(hotRes.data);
      setColdMemories(coldRes.data);
      setArchiveMemories(archiveRes.data);
      setSkills(skillsRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="loading-spinner" data-testid="dashboard-loading"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8" data-testid="dashboard">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700" data-testid="stat-hot-memories">
          <div className="text-gray-400 text-sm mb-2">💡 Memórias HOT</div>
          <div className="text-3xl font-bold text-blue-400">{hotMemories.length}</div>
          <div className="text-xs text-gray-500 mt-1">Expira em 7 dias</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700" data-testid="stat-cold-memories">
          <div className="text-gray-400 text-sm mb-2">❄️ Memórias COLD</div>
          <div className="text-3xl font-bold text-purple-400">{coldMemories.length}</div>
          <div className="text-xs text-gray-500 mt-1">Permanente</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700" data-testid="stat-archive-memories">
          <div className="text-gray-400 text-sm mb-2">🗄️ Arquivo</div>
          <div className="text-3xl font-bold text-gray-400">{archiveMemories.length}</div>
          <div className="text-xs text-gray-500 mt-1">Histórico</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700" data-testid="stat-skills">
          <div className="text-gray-400 text-sm mb-2">🛠️ Skills Ativas</div>
          <div className="text-3xl font-bold text-green-400">{skills.length}</div>
          <div className="text-xs text-gray-500 mt-1">Procedimentos</div>
        </div>
      </div>

      {/* Memories Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">🧠 Memórias</h2>

        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-700">
          <button
            onClick={() => setActiveTab('hot')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'hot'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
            data-testid="tab-hot"
          >
            💡 HOT ({hotMemories.length})
          </button>
          <button
            onClick={() => setActiveTab('cold')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'cold'
                ? 'text-purple-400 border-b-2 border-purple-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
            data-testid="tab-cold"
          >
            ❄️ COLD ({coldMemories.length})
          </button>
          <button
            onClick={() => setActiveTab('archive')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'archive'
                ? 'text-gray-300 border-b-2 border-gray-300'
                : 'text-gray-400 hover:text-gray-300'
            }`}
            data-testid="tab-archive"
          >
            🗄️ ARCHIVE ({archiveMemories.length})
          </button>
        </div>

        {/* Memory Content */}
        <div data-testid="memory-content">
          {activeTab === 'hot' && <MemoryViewer memories={hotMemories} type="hot" />}
          {activeTab === 'cold' && <MemoryViewer memories={coldMemories} type="cold" />}
          {activeTab === 'archive' && <MemoryViewer memories={archiveMemories} type="archive" />}
        </div>
      </div>

      {/* Skills Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4">🛠️ Skills Ativas</h2>
        {skills.length === 0 ? (
          <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
            <p className="text-gray-400">Nenhuma skill criada ainda.</p>
            <p className="text-sm text-gray-500 mt-2">
              Skills são criadas automaticamente quando a IA detecta procedimentos repetíveis.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {skills.map((skill) => (
              <SkillCard key={skill.id} skill={skill} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
