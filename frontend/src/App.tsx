import React from 'react';
import { runResearch } from './api/client';
import SearchBar from './components/SearchBar';
import AgentProgress from './components/AgentProgress';
import ReportView from './components/ReportView';
import HistoryPanel from './components/HistoryPanel';

const App: React.FC = () => {
  const [query, setQuery] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [result, setResult] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [showHistory, setShowHistory] = React.useState(false);

  const handleSearch = async (query: string) => {
    console.log(`[App] Starting search for: ${query}`);
    setQuery(query);
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const researchResult = await runResearch(query);
      setResult(researchResult);
      console.log('[App] Search completed successfully');
    } catch (err) {
      console.error('[App] Search failed:', err);
      setError('Research failed: ' + (err instanceof Error ? err.message : String(err)));
    } finally {
      setIsLoading(false);
      console.log('[App] Search process finished');
    }
  };

  const handleHistorySelect = (synthesis: string) => {
    console.log('[App] History item selected');
    setResult({ synthesis });
    setIsLoading(false);
    setShowHistory(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-50 dark:text-slate-50 flex flex-col min-h-[100vh]">
      {/* Hero Section */}
      <div className="flex-0 flex flex-col items-center justify-center py-12 text-center space-y-4">
        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-violet-600">
          Multi-tool Job Research Agent
        </h1>
        <p className="text-slate-400 max-w-xl">
          Research any company in seconds. Powered by AI agents.
        </p>
        <div className="flex items-center space-x-2 text-xs text-slate-500">
          <span className="w-0.5 h-0.5 bg-slate-600 rounded-full"></span>
          <span>Powered by LangGraph + Groq</span>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex-0 flex items-center justify-center px-6 py-4">
        <SearchBar
          onSearch={handleSearch}
          isLoading={isLoading}
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex-0 w-full px-6 py-4">
          <div className="bg-red-900/50 border border-red-800/50 text-red-300 px-4 py-3 rounded-xl backdrop-blur-sm">
            {error}
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex-1 flex items-center justify-center px-6">
          <AgentProgress isLoading={true} />
        </div>
      )}

      {/* Results */}
      {result && !isLoading && (
        <div className="flex-1 flex items-center justify-center px-6 pb-12">
          <ReportView result={result} />
        </div>
      )}

      {/* History Toggle */}
      <div className="flex-0 flex items-center justify-center px-6 py-4">
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="text-slate-400 hover:text-slate-300 transition-colors font-medium text-sm"
        >
          {showHistory ? 'Hide History' : 'Show History'}
        </button>
      </div>
    </div>
  );
};

export default App;