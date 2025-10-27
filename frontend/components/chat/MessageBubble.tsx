import { Message } from '@/hooks/useChat';

interface MessageBubbleProps {
  message: Message;
  showTranslation?: boolean;
}

export default function MessageBubble({ message, showTranslation = false }: MessageBubbleProps) {
  const isSent = message.type === 'sent';

  return (
    <div className={`flex ${isSent ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      <div
        className={`max-w-[85%] sm:max-w-[75%] md:max-w-[65%] rounded-2xl px-4 py-3 shadow-sm ${
          isSent
            ? 'bg-blue-600 text-white rounded-br-sm'
            : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm'
        }`}
      >
        {/* 원문 */}
        <p className="text-sm sm:text-base leading-relaxed break-words">
          {message.text}
        </p>

        {/* 번역문 (있을 경우) */}
        {showTranslation && message.translated && (
          <div className={`mt-2 pt-2 border-t text-xs sm:text-sm opacity-80 ${
            isSent ? 'border-blue-400' : 'border-gray-200'
          }`}>
            <span className="font-semibold block mb-1">번역:</span>
            <p className="leading-relaxed">{message.translated}</p>
          </div>
        )}

        {/* 타임스탬프 */}
        <div className="flex items-center justify-end gap-2 mt-2">
          <span className={`text-xs ${isSent ? 'text-blue-100' : 'text-gray-500'}`}>
            {new Date(message.timestamp).toLocaleTimeString('ko-KR', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>

          {/* 전송 상태 아이콘 (발신 메시지만) */}
          {isSent && message.status && (
            <span className="text-xs">
              {message.status === 'sending' && '⏳'}
              {message.status === 'sent' && '✓'}
              {message.status === 'delivered' && '✓✓'}
              {message.status === 'error' && '⚠️'}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
