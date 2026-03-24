import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '二重共情ロボット対話システム',
  description: 'AER + CER Dual Empathy Robot Dialogue System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  )
}
