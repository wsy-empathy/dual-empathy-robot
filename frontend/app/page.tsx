'use client';

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Language, translations } from './i18n';

// 在 Vercel 上使用相对路径，本地开发使用 localhost:8000
const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' : '');

interface Message {
  role: 'user' | 'AER' | 'CER' | 'system';
  content: string;
  timestamp?: string;
}

interface Topic {
  key: string;
  ja: string;
  zh: string;
}

interface Subtopic {
  key: string;
  ja: string;
  zh: string;
}

export default function Home() {
  const [language, setLanguage] = useState<Language>('ja');
  const [sessionId, setSessionId] = useState<string>('');
  const [stage, setStage] = useState<'init' | 'topic' | 'subtopic' | 'chat'>('init');
  const [topics, setTopics] = useState<Topic[]>([]);
  const [subtopics, setSubtopics] = useState<Subtopic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [emotion, setEmotion] = useState<{label: string; score: number} | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 获取翻译
  const t = (key: keyof typeof translations.ja) => translations[language][key];

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 自动聚焦输入框
  useEffect(() => {
    if (stage === 'chat') {
      inputRef.current?.focus();
    }
  }, [stage]);

  // 初始化会话
  const initSession = async () => {
    try {
      setIsLoading(true);
      const response = await axios.post(`${API_URL}/api/session/create`, { user_id: language });
      setSessionId(response.data.session_id);
      setMessages([{ role: 'system', content: response.data.message }]);
      
      // 获取topics
      const topicsResponse = await axios.get(`${API_URL}/api/topics?lang=${language}`);
      setTopics(topicsResponse.data.topics);
      setStage('topic');
    } catch (error) {
      console.error('Error initializing session:', error);
      alert(t('errorInit'));
    } finally {
      setIsLoading(false);
    }
  };

  // 选择topic
  const selectTopic = async (topicKey: string) => {
    try {
      setIsLoading(true);
      const response = await axios.post(`${API_URL}/api/session/select-topic`, {
        session_id: sessionId,
        topic_key: topicKey,
        language: language
      });
      
      setSelectedTopic(topicKey);
      setMessages(prev => [...prev, { role: 'system', content: response.data.message }]);
      setSubtopics(response.data.subtopics.map((st: any) => ({
        key: st[0],
        ja: st[1],
        zh: st[2]
      })));
      setStage('subtopic');
    } catch (error) {
      console.error('Error selecting topic:', error);
      alert(t('errorTopic'));
    } finally {
      setIsLoading(false);
    }
  };

  // 选择subtopic
  const selectSubtopic = async (subtopicKey: string) => {
    try {
      setIsLoading(true);
      const response = await axios.post(`${API_URL}/api/session/select-subtopic`, {
        session_id: sessionId,
        subtopic_key: subtopicKey,
        language: language
      });
      
      setMessages(prev => [...prev, { role: 'system', content: response.data.message }]);
      setStage('chat');
    } catch (error) {
      console.error('Error selecting subtopic:', error);
      alert(t('errorSubtopic'));
    } finally {
      setIsLoading(false);
    }
  };

  // 发送消息
  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage = inputText;
    setInputText('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage, timestamp: new Date().toISOString() }]);

    try {
      setIsLoading(true);
      const response = await axios.post(`${API_URL}/api/chat`, {
        session_id: sessionId,
        message: userMessage,
        language: language
      });

      // 添加机器人回应
      setMessages(prev => [...prev, {
        role: response.data.agent as 'AER' | 'CER' | 'system',
        content: response.data.response || response.data.message,
        timestamp: new Date().toISOString()
      }]);

      // 更新情绪信息
      if (response.data.emotion) {
        setEmotion(response.data.emotion);
      }

      // 检查是否完成
      if (response.data.is_completed) {
        setTimeout(() => {
          if (confirm(language === 'ja' ? '対話が完了しました。新しいセッションを開始しますか？' : '对话已完成。要开始新会话吗？')) {
            window.location.reload();
          }
        }, 1000);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert(t('errorSend'));
    } finally {
      setIsLoading(false);
    }
  };

  // Topic图标映射
  const getTopicEmoji = (key: string) => {
    const emojiMap: Record<string, string> = {
      'academic': '📚',
      'financial': '💰',
      'relationship': '👥',
      'future': '🎯'
    };
    return emojiMap[key] || '💭';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-pink-50">
      {/* 顶部导航栏 */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-pink-500 flex items-center justify-center text-white font-bold text-lg shadow-md">
              🤖
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-800">双共情机器人</h1>
              <p className="text-xs text-gray-500">AER 💖 + CER 🧠</p>
            </div>
          </div>
          
          {/* 语言切换 */}
          <div className="flex gap-2 bg-gray-100 rounded-full p-1">
            <button
              onClick={() => setLanguage('ja')}
              className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-all duration-200 ${
                language === 'ja' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              🇯🇵 日本語
            </button>
            <button
              onClick={() => setLanguage('zh')}
              className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-all duration-200 ${
                language === 'zh' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              🇨🇳 中文
            </button>
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <main className="pt-20 pb-6 px-4 sm:px-6 max-w-5xl mx-auto">
        
        {/* 初始页面 */}
        {stage === 'init' && (
          <div className="flex flex-col items-center justify-center py-16 space-y-8 animate-fade-in">
            <div className="text-center space-y-4">
              <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-blue-400 to-pink-400 flex items-center justify-center text-5xl shadow-xl animate-bounce-slow">
                💬
              </div>
              <h2 className="text-3xl font-bold text-gray-800">
                {language === 'ja' ? 'こんにちは' : '你好'}
              </h2>
              <p className="text-gray-600 max-w-md">
                {language === 'ja' 
                  ? '私たちは、あなたの気持ちに寄り添う共感ロボットです。' 
                  : '我们是双共情机器人，会倾听和理解你的感受。'}
              </p>
            </div>
            
            <button
              onClick={initSession}
              disabled={isLoading}
              className="group relative px-8 py-4 bg-gradient-to-r from-blue-500 to-pink-500 text-white rounded-full font-semibold text-lg shadow-lg hover:shadow-xl hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
            >
              <span className="flex items-center space-x-2">
                <span>{isLoading ? (language === 'ja' ? '準備中...' : '准备中...') : (language === 'ja' ? '会話を始める' : '开始对话')}</span>
                {!isLoading && <span className="group-hover:translate-x-1 transition-transform">→</span>}
              </span>
            </button>
            
            <div className="grid grid-cols-2 gap-4 mt-12 max-w-2xl w-full">
              <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-4 text-center shadow-md border border-gray-100">
                <div className="text-3xl mb-2">💖</div>
                <div className="text-sm font-semibold text-gray-800">AER</div>
                <div className="text-xs text-gray-600 mt-1">{language === 'ja' ? '感情共感' : '情感共鸣'}</div>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-4 text-center shadow-md border border-gray-100">
                <div className="text-3xl mb-2">🧠</div>
                <div className="text-sm font-semibold text-gray-800">CER</div>
                <div className="text-xs text-gray-600 mt-1">{language === 'ja' ? '認知共感' : '认知共鸣'}</div>
              </div>
            </div>
          </div>
        )}

        {/* 话题选择 */}
        {stage === 'topic' && (
          <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">{t('selectTopic')}</h2>
              <p className="text-gray-600 text-sm">{language === 'ja' ? 'お話ししたいテーマを選んでください' : '请选择你想聊的主题'}</p>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {topics.map((topic, index) => (
                <button
                  key={topic.key}
                  onClick={() => selectTopic(topic.key)}
                  disabled={isLoading}
                  className="group relative bg-white hover:bg-gradient-to-br hover:from-blue-50 hover:to-pink-50 rounded-2xl p-6 text-left border-2 border-gray-100 hover:border-blue-300 hover:shadow-lg disabled:opacity-50 transition-all duration-300 animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="flex items-center space-x-4">
                    <div className="text-4xl">{getTopicEmoji(topic.key)}</div>
                    <div className="flex-1">
                      <div className="font-bold text-gray-800 group-hover:text-blue-600 transition-colors text-lg">
                        {topic[language]}
                      </div>
                    </div>
                    <div className="text-gray-400 group-hover:text-blue-500 group-hover:translate-x-1 transition-all">→</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 子话题选择 */}
        {stage === 'subtopic' && (
          <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">{t('selectSubtopic')}</h2>
              <p className="text-gray-600 text-sm">{language === 'ja' ? 'より具体的にお選びください' : '请选择更具体的内容'}</p>
            </div>
            
            <div className="space-y-3">
              {subtopics.map((subtopic, index) => (
                <button
                  key={subtopic.key}
                  onClick={() => selectSubtopic(subtopic.key)}
                  disabled={isLoading}
                  className="w-full group bg-white hover:bg-gradient-to-r hover:from-blue-50 hover:to-white rounded-xl p-4 text-left border-2 border-gray-100 hover:border-blue-300 hover:shadow-md disabled:opacity-50 transition-all duration-300 animate-slide-up"
                  style={{ animationDelay: `${index * 80}ms` }}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-gray-800 group-hover:text-blue-600 transition-colors">
                      {subtopic[language]}
                    </span>
                    <span className="text-gray-400 group-hover:text-blue-500 group-hover:translate-x-1 transition-all">→</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 聊天界面 */}
        {stage === 'chat' && (
          <div className="max-w-4xl mx-auto space-y-4 animate-fade-in">
            {/* 情绪显示卡片 */}
            {emotion && (
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl p-4 shadow-sm animate-slide-down">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">😊</div>
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-gray-700">
                      {language === 'ja' ? '感情の状態' : '情绪状态'}
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="px-3 py-1 bg-yellow-200 rounded-full text-sm font-semibold text-yellow-800">
                        {emotion.label}
                      </span>
                      <span className="text-sm text-gray-600">
                        {(emotion.score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 消息容器 */}
            <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="h-[500px] overflow-y-auto p-6 space-y-4 custom-scrollbar">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-message-appear`}
                  >
                    <div className={`max-w-[75%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                      {/* Agent 头像和名称 */}
                      {msg.role !== 'user' && (
                        <div className="flex items-center space-x-2 mb-2 ml-2">
                          <div className="text-xl">
                            {msg.role === 'AER' ? '💖' : msg.role === 'CER' ? '🧠' : '🤖'}
                          </div>
                          <span className={`text-xs font-bold ${
                            msg.role === 'AER' ? 'text-pink-600' : msg.role === 'CER' ? 'text-blue-600' : 'text-gray-600'
                          }`}>
                            {msg.role === 'AER' ? 'AER' : msg.role === 'CER' ? 'CER' : 'System'}
                          </span>
                        </div>
                      )}
                      
                      {/* 消息气泡 */}
                      <div className={`rounded-2xl px-5 py-3 shadow-sm ${
                        msg.role === 'user' 
                          ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-tr-sm'
                          : msg.role === 'AER'
                          ? 'bg-gradient-to-br from-pink-100 to-pink-50 text-gray-800 rounded-tl-sm border border-pink-200'
                          : msg.role === 'CER'
                          ? 'bg-gradient-to-br from-blue-100 to-blue-50 text-gray-800 rounded-tl-sm border border-blue-200'
                          : 'bg-gradient-to-br from-gray-100 to-gray-50 text-gray-800 rounded-tl-sm border border-gray-200'
                      }`}>
                        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                          {msg.content}
                        </p>
                      </div>
                      
                      {/* 用户头像 */}
                      {msg.role === 'user' && (
                        <div className="flex items-center justify-end space-x-2 mt-2 mr-2">
                          <span className="text-xs font-semibold text-gray-500">{t('you')}</span>
                          <div className="text-lg">👤</div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {/* 加载指示器 */}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-2xl px-5 py-3 rounded-tl-sm">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* 输入区域 */}
              <div className="border-t border-gray-200 bg-white/90 backdrop-blur-sm p-4">
                <div className="flex items-end space-x-3">
                  <div className="flex-1 relative">
                    <input
                      ref={inputRef}
                      type="text"
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          sendMessage();
                        }
                      }}
                      placeholder={language === 'ja' ? 'メッセージを入力...' : '输入消息...'}
                      disabled={isLoading}
                      className="w-full px-5 py-3 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-all text-sm"
                    />
                  </div>
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !inputText.trim()}
                    className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-blue-500 to-pink-500 text-white rounded-full flex items-center justify-center hover:shadow-lg hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200 font-bold text-lg"
                  >
                    {isLoading ? '⏳' : '↑'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* CSS动画 */}
      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slide-up {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slide-down {
          from { opacity: 0; transform: translateY(-20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes message-appear {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
        
        @keyframes bounce-slow {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        
        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
        
        .animate-slide-up {
          animation: slide-up 0.5s ease-out backwards;
        }
        
        .animate-slide-down {
          animation: slide-down 0.5s ease-out;
        }
        
        .animate-message-appear {
          animation: message-appear 0.3s ease-out;
        }
        
        .animate-bounce-slow {
          animation: bounce-slow 2s ease-in-out infinite;
        }
        
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e0;
          border-radius: 10px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #a0aec0;
        }
      `}</style>
    </div>
  );
}
