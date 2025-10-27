import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'MedTranslate - 의료 다국어 상담',
  description: '실시간 의료 다국어 번역 상담 서비스',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" className="h-full">
      <body className="h-full antialiased bg-gray-50">
        <div className="min-h-full flex flex-col">
          {children}
        </div>
      </body>
    </html>
  )
}
