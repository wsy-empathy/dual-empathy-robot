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
      ja: `それでは「${topicName}」について一緒に話しましょう。まず、最近のあなたの状況や困っていること、不安に思っていることなどを、できるだけ具体的に教えてもらえますか？例えば、いつ頃からそう感じているか、どんな時に特にそう思うか、など詳しく聞かせてください。`,
      zh: `那我们就一起聊聊「${topicName}」这个话题吧。首先，能不能详细告诉我你最近的情况、遇到的困难或者担心的事情？比如，从什么时候开始有这种感觉、在什么情况下特别明显、具体是怎样的情况等等，请尽可能详细地告诉我。`
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
