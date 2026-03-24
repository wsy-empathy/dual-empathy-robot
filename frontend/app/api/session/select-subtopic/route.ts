import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const language = body.language || 'ja';
    const subtopicKey = body.subtopic_key || '';
    
    // 根据子话题构建更具体的引导
    const subtopicNames: Record<string, Record<string, string>> = {
      exam_anxiety: { ja: "試験不安", zh: "考试焦虑" },
      study_pace: { ja: "学習ペース", zh: "学习节奏" },
      follow_content: { ja: "授業理解", zh: "跟上课程内容" },
      cost_burden: { ja: "経済的負担", zh: "经济负担" },
      work_study_balance: { ja: "バイトと学業", zh: "打工与学业" },
      financial_anxiety: { ja: "お金の不安", zh: "经济焦虑" },
      making_friends: { ja: "友達作り", zh: "交朋友" },
      no_confidant: { ja: "相談相手がいない", zh: "没有倾诉对象" },
      interaction_issues: { ja: "コミュニケーション", zh: "沟通问题" },
      unclear_goals: { ja: "目標が不明確", zh: "目标不明确" },
      career_choice: { ja: "進路選択", zh: "职业选择" },
      preparation: { ja: "就活準備", zh: "就业准备" }
    };
    
    const topicName = subtopicNames[subtopicKey]?.[language] || '';
    
    const startMessages: Record<string, string> = {
      ja: `それでは「${topicName}」について一緒に話しましょう。あなたの状況をよりよく理解するために、最近一番気になった経験について話してください：その感覚はいつ頃から始まったのか、どんな授業や場面で特に顕著なのか、そしてその時具体的にどんな困難や心配に直面するのか、など教えてください。`,
      zh: `那我们接下来可以一起聊聊"${topicName}"这件事。为了更好地理解你的情况，你可以和我说说最近让你最在意的经历：这种感觉大概是从什么时候开始的，通常会在什么课程或场景里更明显，以及你当时具体会遇到哪些困难或担心。`
    };
    
    return NextResponse.json({
      message: startMessages[language] || startMessages.ja
    });
  } catch (error) {
    console.error('Subtopic selection error:', error);
    return NextResponse.json(
      { error: 'Failed to select subtopic' },
      { status: 500 }
    );
  }
}
