import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const lang = searchParams.get('lang') || 'ja';
  
  const topicsData: Record<string, any[]> = {
    ja: [
      { key: "academic", name: "学業の問題", ja: "学業の問題", zh: "学业问题" },
      { key: "financial", name: "経済的な問題", ja: "経済的な問題", zh: "经济问题" },
      { key: "relationship", name: "人間関係", ja: "人間関係", zh: "人际关系" },
      { key: "future", name: "将来設計", ja: "将来設計", zh: "未来规划" }
    ],
    zh: [
      { key: "academic", name: "学业问题", ja: "学業の問題", zh: "学业问题" },
      { key: "financial", name: "经济问题", ja: "経済的な問題", zh: "经济问题" },
      { key: "relationship", name: "人际关系", ja: "人間関係", zh: "人际关系" },
      { key: "future", name: "未来规划", ja: "将来設計", zh: "未来规划" }
    ]
  };
  
  return NextResponse.json({
    topics: topicsData[lang] || topicsData.ja
  });
}
