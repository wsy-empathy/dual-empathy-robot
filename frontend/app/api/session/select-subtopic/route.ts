import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const language = body.language || 'ja';
    
    const startMessages: Record<string, string> = {
      ja: "それでは、あなたの気持ちを聞かせてください。",
      zh: "那么，请告诉我你的感受吧。"
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
