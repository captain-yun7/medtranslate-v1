'use client';

import { useState, useEffect } from 'react';

interface LanguageSelectorProps {
  value: string;
  onChange: (language: string) => void;
  disabled?: boolean;
}

const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'th', name: 'ภาษาไทย', flag: '🇹🇭' },
  { code: 'vi', name: 'Tiếng Việt', flag: '🇻🇳' },
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
];

export default function LanguageSelector({ value, onChange, disabled = false }: LanguageSelectorProps) {
  // 로컬스토리지에서 언어 불러오기
  useEffect(() => {
    const savedLanguage = localStorage.getItem('medtranslate_language');
    if (savedLanguage && savedLanguage !== value) {
      onChange(savedLanguage);
    }
  }, []);

  const handleChange = (newLanguage: string) => {
    // 로컬스토리지에 저장
    localStorage.setItem('medtranslate_language', newLanguage);
    onChange(newLanguage);
  };

  const selectedLanguage = languages.find((lang) => lang.code === value);

  return (
    <div className="relative">
      <label className="block text-xs font-medium text-gray-700 mb-1.5">
        내 언어 선택
      </label>
      <select
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        disabled={disabled}
        className="w-full p-2.5 pl-3 pr-10 border border-gray-300 rounded-lg bg-white text-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          disabled:bg-gray-100 disabled:cursor-not-allowed
          appearance-none cursor-pointer
          transition-all duration-200"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236B7280'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 0.5rem center',
          backgroundSize: '1.25rem',
        }}
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>

      {selectedLanguage && (
        <div className="mt-1.5 text-xs text-gray-500 flex items-center gap-1">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          메시지가 자동으로 번역됩니다
        </div>
      )}
    </div>
  );
}
