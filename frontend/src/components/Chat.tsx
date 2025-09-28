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
      
      const errorBotMessage: Message = {
        id: generateId(),
        content: `❌ Sorry, I encountered an error: ${errorMessage}`,
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
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header - Clean and Simple */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <Heart className="h-8 w-8 text-red-500" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                ArogyaAI
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
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
        <div className="flex-1 flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 overflow-hidden">
          
          {/* Chat Header */}
          <div className="bg-blue-600 dark:bg-blue-700 text-white px-6 py-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
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
                <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
                  Welcome to ArogyaAI!
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
                  I&apos;m your intelligent health assistant. I can provide information about diseases, symptoms, treatments, and WHO guidelines in multiple languages.
                </p>
                <div className="mb-6">
                  <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full text-sm">
                    <span className="text-lg">🌍</span>
                    <span>Supports 15+ languages automatically</span>
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
          <div className="border-t border-gray-200 dark:border-gray-700">
            <ChatInput 
              onSendMessage={handleSendMessage} 
              loading={loading} 
            />
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
              <AlertCircle className="h-5 w-5" />
              <span className="flex-1">{error}</span>
              <button
                onClick={() => setError(null)}
                className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
              >
                ✕
              </button>
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
