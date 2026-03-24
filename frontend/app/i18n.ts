/**
 * 多语言配置文件
 */

export type Language = 'ja' | 'zh';

export const translations = {
  ja: {
    // 标题和通用文本
    title: '二重共情ロボットシステム',
    startButton: '対話を開始',
    loading: '読み込み中...',
    sending: '送信中...',
    inputPlaceholder: 'メッセージを入力してください...',
    send: '送信',
    restart: '最初から',
    
    // 话题选择
    selectTopic: 'まず、下記から一つ選んでください',
    selectSubtopic: '具体的な内容を選んでください',
    
    // Agent标签
    aer: 'AER',
    cer: 'CER',
    system: 'システム',
    you: 'あなた',
    
    // 阶段提示
    stage: 'ステージ',
    completed: '完了',
    
    // 情感分析
    emotion: '感情',
    sentiment: '感情分析',
    
    // 错误消息
    errorInit: 'セッションの初期化に失敗しました',
    errorTopic: 'トピック選択に失敗しました',
    errorSubtopic: 'サブトピック選択に失敗しました',
    errorSend: 'メッセージ送信に失敗しました',
    
    // 完成消息
    congratulations: 'お疲れ様でした！',
    sessionComplete: '対話が完了しました。ご協力ありがとうございました。',
  },
  
  zh: {
    // 标题和通用文本
    title: '双重共情机器人系统',
    startButton: '开始对话',
    loading: '加载中...',
    sending: '发送中...',
    inputPlaceholder: '请输入消息...',
    send: '发送',
    restart: '重新开始',
    
    // 话题选择
    selectTopic: '首先，请从下面选择一个话题',
    selectSubtopic: '请选择具体内容',
    
    // Agent标签
    aer: 'AER',
    cer: 'CER',
    system: '系统',
    you: '你',
    
    // 阶段提示
    stage: '阶段',
    completed: '已完成',
    
    // 情感分析
    emotion: '情感',
    sentiment: '情感分析',
    
    // 错误消息
    errorInit: '会话初始化失败',
    errorTopic: '话题选择失败',
    errorSubtopic: '子话题选择失败',
    errorSend: '消息发送失败',
    
    // 完成消息
    congratulations: '恭喜完成！',
    sessionComplete: '对话已完成。感谢您的参与。',
  }
};

export function getTranslation(lang: Language, key: keyof typeof translations.ja): string {
  return translations[lang][key] || translations['ja'][key];
}
