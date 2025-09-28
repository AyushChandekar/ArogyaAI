import { Loader2 } from 'lucide-react';

export default function LoadingIndicator() {
  return (
    <div className="text-left mb-4">
      <div className="inline-block bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
        <div className="flex items-center gap-3 text-gray-600 dark:text-gray-300">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600 dark:text-blue-400" />
          <span className="text-sm">ArogyaAI is thinking...</span>
        </div>
      </div>
    </div>
  );
}
