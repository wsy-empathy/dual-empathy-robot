import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const topicKey = body.topic_key || '';
    const language = body.language || 'ja';
    
    const subtopicsMap: Record<string, string[][]> = {
      academic: [
        ["exam_anxiety", "試験不安", "考试焦虑"],
        ["study_pace", "学習ペース", "学习节奏"],
        ["follow_content", "授業理解", "课程理解"]
      ],
      financial: [
        ["cost_burden", "経済的負担", "经济负担"],
        ["work_study_balance", "バイトと学業", "打工与学业"],
        ["financial_anxiety", "お金の不安", "经济焦虑"]
      ],
      relationship: [
        ["making_friends", "友達作り", "交朋友"],
        ["no_confidant", "相談相手がいない", "没有倾诉对象"],
        ["interaction_issues", "コミュニケーション", "沟通问题"]
      ],
      future: [
        ["unclear_goals", "目標が不明確", "目标不明确"],
        ["career_choice", "進路選択", "职业选择"],
        ["preparation", "就活準備", "就业准备"]
      ]
    };
    
    return NextResponse.json({
      message: language === 'ja' ? "具体的にはどの点が気になりますか？" : "具体来说，哪方面让你困扰？",
      subtopics: subtopicsMap[topicKey] || []
    });
  } catch (error) {
    console.error('Topic selection error:', error);
    return NextResponse.json(
      { error: 'Failed to select topic' },
      { status: 500 }
    );
  }
}
