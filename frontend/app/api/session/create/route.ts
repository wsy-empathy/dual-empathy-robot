import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const language = body.user_id || 'ja';
    const sessionId = Math.random().toString(36).substring(7);
    
    const welcomeMessages: Record<string, string> = {
      ja: "最近、気がかりなことがあれば聞かせてもらえますか？授業のこと、進路のこと、お金のこと、人との関係のことなど、どれからでも大丈夫です。",
      zh: "最近有什么让你担心的事情吗？无论是课程、未来规划、经济问题还是人际关系，都可以和我聊聊。"
    };
    
    return NextResponse.json({
      session_id: sessionId,
      message: welcomeMessages[language] || welcomeMessages.ja,
      language: language
    });
  } catch (error) {
    console.error('Session creation error:', error);
    return NextResponse.json(
      { error: 'Failed to create session' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({ status: 'ok' });
}
