import { ReactNode } from 'react';
import Header from './Header';
import Footer from './Footer';

interface ResponsiveLayoutProps {
  children: ReactNode;
  showHeader?: boolean;
  showFooter?: boolean;
}

export default function ResponsiveLayout({
  children,
  showHeader = true,
  showFooter = true,
}: ResponsiveLayoutProps) {
  return (
    <>
      {showHeader && <Header />}
      <main className="flex-1 w-full">
        {children}
      </main>
      {showFooter && <Footer />}
    </>
  );
}
