export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-4">
        <svg
          className="w-10 h-10 text-blue-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        의료 상담을 시작하세요
      </h3>
      <p className="text-sm text-gray-600 max-w-sm">
        아래 입력창에 메시지를 입력하시면 실시간으로 번역되어 상담사에게 전달됩니다.
      </p>
    </div>
  );
}
