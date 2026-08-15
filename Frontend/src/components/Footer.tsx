import React from 'react';
import { CheckCircle, HelpCircle } from 'lucide-react';

interface FooterProps {
  darkMode: boolean;
  lastSync: Date | null;
}

const Footer: React.FC<FooterProps> = ({ darkMode, lastSync }) => {
  return (
    <footer className={`border-t px-6 py-3 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs ${
      darkMode ? 'bg-gray-900 border-gray-700 text-gray-500' : 'bg-white border-gray-100 text-gray-400'
    }`}>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>All systems operational</span>
        </div>
        <span className={`${darkMode ? 'text-gray-600' : 'text-gray-200'}`}>|</span>
        <span>Last sync: {lastSync ? lastSync.toLocaleTimeString() : '—'}</span>
        <span className={`${darkMode ? 'text-gray-600' : 'text-gray-200'}`}>|</span>
        <div className="flex items-center gap-1">
          <CheckCircle size={11} className="text-emerald-500" />
          <span>Data fresh</span>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <span>Manipal Fintech Analytics v2.4.1</span>
        <a href="#" className="hover:text-indigo-500 transition-colors flex items-center gap-1">
          <HelpCircle size={11} />
          Support
        </a>
        <span>© 2026 Manipal Fintech</span>
      </div>
    </footer>
  );
};

export default Footer;
