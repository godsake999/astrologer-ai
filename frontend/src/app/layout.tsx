import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AstroLogic AI | Modern Mystic Astrology',
  description: 'High-precision astrology combining Western, Vedic, and Burmese Mahabote theories.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Padauk:wght@400;700&display=swap" rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  )
}
