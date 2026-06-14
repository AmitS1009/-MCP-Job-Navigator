import React from 'react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isLoading }) => {
  const [query, setQuery] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      console.log(`[SearchBar] Search triggered with query: "${query}"`);
      onSearch(query);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter company or job topic to research..."
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          className="w-full rounded-2xl border border-slate-700/50 bg-slate-900/50 backdrop-blur-sm px-6 py-4 text-slate-50 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/75 transition-all duration-200"
        />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="absolute right-0 top-0 bottom-0 ml-2 rounded-2xl px-6 py-3 font-semibold text-sm bg-gradient-to-r from-blue-500 to-violet-600 hover:opacity-90 hover:scale-105 transition-all duration-200 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Researching...' : 'Research'}
        </button>
      </div>
    </form>
  );
};

export default SearchBar;