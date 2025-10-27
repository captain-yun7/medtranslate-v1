export default function TypingIndicator() {
  return (
    <div className="flex justify-start animate-fade-in">
      <div className="bg-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
        <div className="flex gap-1.5 items-center">
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
}
