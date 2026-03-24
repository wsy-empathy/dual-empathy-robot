import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const sessionId = body.session_id || '';
    const message = body.message || '';
    const language = body.language || 'ja';
    
    // 简化版响应（演示用）
    const demoResponse = language === 'ja' 
      ? "こんにちは！これは Vercel 上のデモ版です。完全な共感対話機能を使用するには、バックエンドサーバーを起動してください。"
      : "你好！这是 Vercel 上的演示版本。要使用完整的共情对话功能，请启动后端服务器。";
    
    return NextResponse.json({
      session_id: sessionId,
      agent: "AER",
      response: demoResponse,
      message: demoResponse,
      emotion: null,
      stage: "aer_1"
    });
  } catch (error) {
    console.error('Chat error:', error);
    return NextResponse.json(
      { error: 'Failed to process message' },
      { status: 500 }
    );
  }
}
