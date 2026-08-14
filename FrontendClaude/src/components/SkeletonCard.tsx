import React from 'react';

interface SkeletonCardProps {
  darkMode: boolean;
  height?: string;
}

const SkeletonCard: React.FC<SkeletonCardProps> = ({ darkMode, height = 'h-32' }) => {
  return (
    <div className={`rounded-2xl border p-5 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'} overflow-hidden`}>
      <div className={`animate-pulse space-y-3`}>
        <div className={`h-8 w-8 rounded-xl ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`} />
        <div className={`h-6 w-24 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`} />
        <div className={`h-3 w-32 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`} />
        <div className={`${height} rounded-xl ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`} />
      </div>
    </div>
  );
};

export default SkeletonCard;
