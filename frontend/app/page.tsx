'use client';

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Language, translations } from './i18n';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

  // 获取翻译
  const t = (key: keyof typeof translations.ja) => translations[language][key];

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 初始化会话
  const initSession = async () => {
    try {
      setIsLoading(true);
      const response = await axios.post(`${API_URL}/api/session/create`, { user_id: language });
      setSessionId(response.data.session_id);
      setMessages([{ role: 'system', content: response.data.message }]);
      
      // 获取topics
      const topicsResponse = await axios.get(`${API_URL}/api/topics`);
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
        topic_key: topicKey
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
        subtopic_key: subtopicKey
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
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      setIsLoading(true);
      const response = await axios.post(`${API_URL}/api/chat`, {
        session_id: sessionId,
        message: userMessage
      });

      // 添加机器人回应
      setMessages(prev => [...prev, {
        role: response.data.agent as 'AER' | 'CER' | 'system',
        content: response.data.message
      }]);

      // 更新情绪信息
      if (response.data.emotion) {
        setEmotion(response.data.emotion);
      }

      // 检查是否完成
      if (response.data.is_completed) {
        setTimeout(() => {
          if (confirm('対話が完了しました。新しいセッションを開始しますか？')) {
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

  // 获取消息样式
  const getMessageClass = (role: string) => {
    switch (role) {
      case 'AER':
        return 'message-aer';
      case 'CER':
        return 'message-cer';
      case 'user':
        return 'message-user';
      case 'system':
        return 'message-system';
      default:
        return '';
    }
  };

  // 获取Agent标签
  const getAgentBadge = (role: string) => {
    switch (role) {
      case 'AER':
        return <span className="inline-block px-3 py-1 bg-aer text-white rounded-full text-sm font-bold mr-2">{t('aer')}</span>;
      case 'CER':
        return <span className="inline-block px-3 py-1 bg-cer text-white rounded-full text-sm font-bold mr-2">{t('cer')}</span>;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">{t('title')}</h1>
            <p className="text-sm text-gray-600 mt-1">AER（情感共情）+ CER（認知共情）</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setLanguage('ja')}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                language === 'ja' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              日本語
            </button>
            <button
              onClick={() => setLanguage('zh')}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                language === 'zh' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              中文
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        {stage === 'init' && (
          <div className="text-center py-12">
            <button
              onClick={initSession}
              disabled={isLoading}
              className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 text-lg font-semibold"
            >
              {isLoading ? t('loading') : t('startButton')}
            </button>
          </div>
        )}

        {stage === 'topic' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">{t('selectTopic')}</h2>
            <div className="grid grid-cols-1 gap-3">
              {topics.map(topic => (
                <button
                  key={topic.key}
                  onClick={() => selectTopic(topic.key)}
                  disabled={isLoading}
                  className="p-4 text-left border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 disabled:opacity-50 transition"
                >
                  <div className="font-semibold text-gray-800">{topic[language]}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {stage === 'subtopic' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">{t('selectSubtopic')}</h2>
            <div className="grid grid-cols-1 gap-3">
              {subtopics.map(subtopic => (
                <button
                  key={subtopic.key}
                  onClick={() => selectSubtopic(subtopic.key)}
                  disabled={isLoading}
                  className="p-4 text-left border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 disabled:opacity-50 transition"
                >
                  <div className="font-semibold text-gray-800">{subtopic[language]}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {stage === 'chat' && (
          <div className="space-y-4">
            {/* 情绪显示 */}
            {emotion && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <span className="text-sm font-semibold">{t('emotion')}:</span>
                <span className="ml-2 px-2 py-1 bg-yellow-200 rounded text-sm">
                  {emotion.label} ({(emotion.score * 100).toFixed(1)}%)
                </span>
              </div>
            )}

            {/* 消息列表 */}
            <div className="bg-white rounded-lg shadow-md p-4 min-h-[500px] max-h-[600px] overflow-y-auto">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`mb-4 p-4 rounded-lg ${getMessageClass(msg.role)}`}
                >
                  <div className="flex items-center mb-2">
                    {getAgentBadge(msg.role)}
                    {msg.role === 'user' && (
                      <span className="text-sm font-semibold text-gray-700">{t('you')}</span>
                    )}
                  </div>
                  <div className="text-gray-800 whitespace-pre-wrap">{msg.content}</div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* 输入框 */}
            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder={t('inputPlaceholder')}
                  disabled={isLoading}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 disabled:bg-gray-100"
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !inputText.trim()}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-semibold"
                >
                  {isLoading ? t('sending') : t('send')}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-gray-600 text-sm">
        <p>Dual Empathy Robot System v2.0 | AER + CER</p>
      </footer>
    </div>
  );
}
