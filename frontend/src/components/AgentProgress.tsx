import React from 'react';

interface AgentProgressProps {
  isLoading: boolean;
}

const AgentProgress: React.FC<AgentProgressProps> = ({ isLoading }) => {
  React.useEffect(() => {
    if (isLoading) {
      console.log('[AgentProgress] Component mounted');
    }
    return () => {
      console.log('[AgentProgress] Component unmounted');
    };
  }, [isLoading]);

  if (!isLoading) {
    return null;
  }

  const agents = [
    { name: 'News Agent', emoji: '📰' },
    { name: 'Jobs Agent', emoji: '💼' },
    { name: 'Company Agent', emoji: '🏢' },
    { name: 'Competitor Agent', emoji: '🆚' },
    { name: 'Synthesis Agent', emoji: '🔬' },
    { name: 'Validation Agent', emoji: '✅' }
  ];

  return (
    <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6 w-full max-w-xl">
      <div className="flex items-center space-x-3 mb-4">
        <span className="text-2xl">⚡</span>
        <h3 className="text-lg font-semibold text-slate-50">
          Agents working<span className="animate-pulse">.</span>
        </h3>
      </div>
      <div className="space-y-3">
        {agents.map((agent, index) => (
          <div
            key={index}
            className={`flex items-center space-x-3 opacity-0 animate-fade-in-up-${index + 1}`}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <span className="text-2xl">{agent.emoji}</span>
            <div className="flex-1">
              <p className="text-slate-400 font-medium">{agent.name}</p>
              <div className="w-full h-2.5 bg-slate-900/50 rounded-full overflow-hidden mt-1">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-violet-600 bg-gradient-to-l animate-[gradient-shift_8s_ease_infinite] rounded-full"
                  style={{ backgroundSize: '200% 200%' }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentProgress;