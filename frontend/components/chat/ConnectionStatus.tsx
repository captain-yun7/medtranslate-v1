interface ConnectionStatusProps {
  isConnected: boolean;
  isReconnecting?: boolean;
}

export default function ConnectionStatus({ isConnected, isReconnecting = false }: ConnectionStatusProps) {
  if (isReconnecting) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-yellow-50 border-b border-yellow-200 text-yellow-800 text-sm">
        <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
        <span>재연결 중...</span>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-red-50 border-b border-red-200 text-red-800 text-sm">
        <div className="w-2 h-2 bg-red-500 rounded-full" />
        <span>연결이 끊어졌습니다</span>
      </div>
    );
  }

  return null;
}
