import React from 'react';
import { getHistory } from '../api/client';

interface HistoryPanelProps {
  onSelect: (synthesis: string) => void;
}

const HistoryPanel: React.FC<HistoryPanelProps> = ({ onSelect }) => {
  const [history, setHistory] = React.useState<Array<any>>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const loadHistory = async () => {
      console.log('[HistoryPanel] Loading history');
      setLoading(true);
      try {
        const data = await getHistory();
        // Take only last 10 sessions
        const recentHistory = data.slice(0, 10);
        setHistory(recentHistory);
        console.log(`[HistoryPanel] History loaded: ${recentHistory.length} items`);
      } catch (err) {
        console.error('[HistoryPanel] Error loading history:', err);
        setError('Failed to load history');
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, []);

  const handleSelect = (item: any) => {
    console.log(`[HistoryPanel] Item selected: ${item.query}`);
    onSelect(item.synthesis);
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-slate-900/75 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="text-slate-400">Loading history...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-slate-900/75 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="text-red-300">{error}</div>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="fixed inset-0 bg-slate-900/75 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="text-slate-400 text-center">No history available</div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-slate-900/75 backdrop-blur-sm z-50">
      {/* Overlay for closing */}
      <div
        className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
        onClick={() => /* Close on overlay click - handled by parent */}
      />
      {/* Sidebar */}
      <div className="relative flex h-full w-full max-w-md slide-in-right">
        <div className="flex-1 flex flex-col bg-slate-800/50 backdrop-blur border-r border-slate-700/50">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/50">
            <h3 className="text-lg font-semibold text-slate-50">Recent Searches</h3>
            <button
              onClick={() => /* Close - handled by parent */}
              className="text-slate-400 hover:text-slate-300 transition-colors"
            >
              ✕
            </button>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto space-y-3 px-4">
            {history.map((item) => (
              <div
                key={item.session_id}
                onClick={() => handleSelect(item)}
                className="cursor-pointer bg-slate-900/50 hover:bg-slate-800/50 transition-colors duration-200 rounded-xl px-4 py-3 flex items-center space-x-3"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-slate-50 font-medium truncate max-w-[200px]">
                    {item.query}
                  </p>
                  <p className="text-slate-400 text-xs truncate">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`w-2 h-2 rounded-full ${
                    item.validation_passed ? 'bg-green-400' : 'bg-amber-400'
                  }`}></span>
                  <span className={`text-xs font-medium ${
                    item.validation_passed ? 'text-green-400' : 'text-amber-400'
                  }`}>
                    {item.validation_passed ? 'Validated' : 'Low confidence'}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-slate-700/50">
            <p className="text-slate-500 text-xs">
              Showing last {history.length} searches
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HistoryPanel;