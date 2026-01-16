import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { MSWComponent } from '@/components/MSWComponent'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Pro-NLP Job Manager',
  description: 'AI-powered Job Application Manager',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <MSWComponent>
          {children}
        </MSWComponent>
      </body>
    </html>
  )
}
