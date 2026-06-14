import React from 'react';
import ReactMarkdown from 'react-markdown';

interface ReportViewProps {
  result: ResearchResult;
}

const ReportView: React.FC<ReportViewProps> = ({ result }) => {
  console.log(`[ReportView] Rendering report for session: ${result.session_id}`);

  return (
    <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-8 w-full max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-slate-50">
          {result.company_name} Research Report
        </h1>
        <div className="flex items-center space-x-4">
          <span className={`px-3 py-1.5 rounded-full text-sm font-medium ${
            result.validation_passed ? 'bg-gradient-to-r from-green-500 to-emerald-600' : 'bg-gradient-to-r from-amber-400 to-amber-500'
          } text-slate-50`}>
            {result.validation_passed ? 'Validated' : 'Low confidence'}
          </span>
          <span className="w-0.5 h-0.5 bg-slate-600 rounded-full"></span>
          <div className="flex items-center space-x-2 text-slate-400 text-sm">
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
              <span>{result.total_results} sources</span>
            </span>
            <span className="w-0.5 h-0.5 bg-slate-600 rounded-full"></span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-violet-500 rounded-full"></span>
              <span>{result.elapsed_seconds.toFixed(1)}s</span>
            </span>
          </div>
          {result.retry_count > 0 && (
            <span className="ml-3 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/20 text-amber-400">
              Retries: {result.retry_count}
            </span>
          )}
        </div>
      </div>

      <div className="prose prose-lg max-w-none text-slate-400">
        <ReactMarkdown
          className="prose-invert"
          overrides={{
            strong: {
              className: 'text-slate-50 font-semibold'
            },
            a: {
              className: 'text-blue-300 hover:text-blue-200 underline decoration-blue-500/50'
            },
            h1: {
              className: 'text-2xl font-bold text-slate-50 mt-8 mb-4'
            },
            h2: {
              className: 'text-xl font-semibold text-blue-400 mt-6 mb-3 border-b border-slate-700/50 pb-2'
            },
            h3: {
              className: 'text-lg font-semibold text-slate-50 mt-5 mb-2'
            },
            ul: {
              className: 'list-disc pl-5 space-y-2'
            },
            li: {
              className: 'flex items-start space-x-3'
            },
            'li::before': {
              content: '"▸"',
              className: 'text-blue-400 flex-shrink-0 mt-0.5'
            },
            pre: {
              className: 'bg-slate-900/50 rounded-xl p-4 border border-slate-700/50'
            },
            code: {
              className: 'text-sm bg-slate-900/50 px-1.5 py-0.5 rounded'
            }
          }}
        >
          {result.synthesis}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default ReportView;