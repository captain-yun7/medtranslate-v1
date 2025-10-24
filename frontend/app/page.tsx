export default function Home() {
  return (
    <div className="flex items-center justify-center h-screen bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          MedTranslate
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          의료 다국어 상담 서비스
        </p>
        <a
          href="/chat/room_001"
          className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          상담 시작하기
        </a>
      </div>
    </div>
  );
}
