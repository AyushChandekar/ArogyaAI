'use client';

import { useState, useEffect, useRef } from 'react';
import { AlertCircle, Heart } from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import LoadingIndicator from './LoadingIndicator';
import ExampleQueries from './ExampleQueries';
import ThemeToggle from './ThemeToggle';
import { apiClient } from '@/lib/api';
import { Message } from '@/types/api';
import { generateId } from '@/lib/utils';

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showExamples, setShowExamples] = useState(true);
  const [lastDetectedLanguage, setLastDetectedLanguage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // No initial welcome message - let the welcome screen handle it

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (messageText: string) => {
    const userMessage: Message = {
      id: generateId(),
      content: messageText,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setShowExamples(false);
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.query({
        query: messageText,
        user_id: 'web_user',
      });

      if (response.status === 'success' && response.response) {
        // Update detected language info
        if (response.detected_language) {
          setLastDetectedLanguage(response.detected_language);
        }
        
        // Create response message with language info if translated
        let responseContent = response.response;
        if (response.was_translated && response.detected_language && response.detected_language !== 'English') {
          responseContent = `🌍 *Detected Language: ${response.detected_language}*\n\n${response.response}`;
        }
        
        const botMessage: Message = {
          id: generateId(),
          content: responseContent,
          isUser: false,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        throw new Error(response.message || 'Failed to get response');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setError(errorMessage);
      
      // Show user-friendly error message with refresh suggestion
      const isConnectionError = errorMessage.includes('timed out') || 
                               errorMessage.includes('Connection failed') || 
                               errorMessage.includes('server is starting up');
      
      const friendlyMessage = isConnectionError 
        ? `🔄 **Connection Issue**: The server might be starting up or there's a network issue.\n\n**Quick Fix**: Please refresh this page and try again. This usually resolves the issue!\n\n*Technical details: ${errorMessage}*`
        : `❌ Sorry, I encountered an error: ${errorMessage}`;
      
      const errorBotMessage: Message = {
        id: generateId(),
        content: friendlyMessage,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorBotMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectQuery = (query: string) => {
    handleSendMessage(query);
  };

  return (
    <div className="h-screen flex flex-col" style={{backgroundColor: 'var(--background)', color: 'var(--foreground)'}}>
      {/* Header - Clean and Simple */}
      <header className="border-b px-4 py-4" style={{backgroundColor: 'var(--background)', borderColor: 'var(--border)'}}>
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <Heart className="h-8 w-8 text-red-500" />
            <div>
              <h1 className="text-2xl font-bold" style={{color: 'var(--foreground)'}}>
                ArogyaAI
              </h1>
              <p className="text-sm opacity-70" style={{color: 'var(--foreground)'}}>
                Intelligent Health Assistant
              </p>
            </div>
          </div>
          
          {/* Theme Toggle */}
          <ThemeToggle />
        </div>
      </header>

      {/* Main Chat Area - Takes remaining height */}
      <main className="flex-1 flex flex-col min-h-0 max-w-4xl mx-auto w-full p-4">
        <div className="flex-1 flex flex-col rounded-lg shadow-md border overflow-hidden" style={{backgroundColor: 'var(--background)', borderColor: 'var(--border)'}}>
          
          {/* Chat Header */}
          <div className="bg-blue-600 dark:bg-blue-700 text-white px-6 py-4 heading">
            <h2 className="text-lg font-semibold flex items-center gap-2 ">
              💬 Chat with ArogyaAI
              {loading && <div className="w-2 h-2 bg-white rounded-full animate-ping" />}
              <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
                🌍 Multilingual
              </span>
            </h2>
            <p className="text-blue-100 text-sm mt-1">
              Ask me about diseases, symptoms, treatments, and more in any language!
              {lastDetectedLanguage && lastDetectedLanguage !== 'English' && (
                <span className="ml-2 text-yellow-200">
                  Last detected: {lastDetectedLanguage}
                </span>
              )}
            </p>
          </div>

          {/* Messages Area - Scrollable */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 chat-messages">
            {messages.length === 0 && !loading ? (
              /* Welcome Message */
              <div className="text-center py-12">
                <Heart className="h-12 w-12 text-red-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2" style={{color: 'var(--foreground)'}}>
                  Welcome to ArogyaAI!
                </h3>
                <p className="opacity-70 mb-6 max-w-md mx-auto" style={{color: 'var(--foreground)'}}>
                  I&apos;m your intelligent health assistant. I can provide information about diseases, symptoms, treatments, and WHO guidelines in multiple languages.
                </p>
                <div className="mb-6">
                  <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 rounded-full text-sm ">
                    <span className="text-lg">🌍</span>
                    <span className="language-support-text">Supports 15+ languages automatically</span>
                  </div>
                </div>
                
                {/* Example Queries */}
                {showExamples && (
                  <div className="mt-8">
                    <ExampleQueries onSelectQuery={handleSelectQuery} />
                  </div>
                )}
              </div>
            ) : (
              /* Chat Messages */
              <>
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}
                {loading && <LoadingIndicator />}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input Area - Fixed at bottom */}
          <div className="border-t" style={{borderColor: 'var(--border)'}}>
            <ChatInput 
              onSendMessage={handleSendMessage} 
              loading={loading} 
            />
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex items-start gap-2 text-red-800 dark:text-red-200">
              <AlertCircle className="h-5 w-5 mt-0.5" />
              <div className="flex-1">
                <span>{error}</span>
                {(error.includes('timed out') || error.includes('Connection failed') || error.includes('server is starting up')) && (
                  <div className="mt-3 flex gap-2">
                    <button
                      onClick={() => window.location.reload()}
                      className="px-3 py-1 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:hover:bg-blue-800 text-blue-800 dark:text-blue-200 rounded text-sm font-medium transition-colors"
                    >
                      🔄 Refresh Page
                    </button>
                    <button
                      onClick={() => setError(null)}
                      className="px-3 py-1 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded text-sm transition-colors"
                    >
                      Dismiss
                    </button>
                  </div>
                )}
              </div>
              {!(error.includes('timed out') || error.includes('Connection failed') || error.includes('server is starting up')) && (
                <button
                  onClick={() => setError(null)}
                  className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer - Compact */}
      <footer className="bg-gray-800 dark:bg-gray-900 text-white py-3">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="text-xs text-gray-300 space-y-1">
            <p>
              <span className="text-yellow-400">⚠️</span>
              <strong> Medical Disclaimer:</strong> This provides general information only.
              Always consult healthcare professionals.
            </p>
            <p>
              <span className="text-red-400">📞</span>
              <strong> Emergency:</strong> Contact local emergency services immediately!
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
