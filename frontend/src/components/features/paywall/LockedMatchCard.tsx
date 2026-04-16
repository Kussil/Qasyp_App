export function LockedMatchCard() {
  return (
    <div className="rounded-lg bg-white border border-gray-200 p-4 relative overflow-hidden">
      <div className="filter blur-sm">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-2/3"></div>
      </div>
      <div className="absolute inset-0 flex items-center justify-center bg-white/60">
        <div className="text-center">
          <div className="text-2xl mb-1">🔒</div>
          <span className="text-xs text-gray-500 font-medium">Заблокировано</span>
        </div>
      </div>
    </div>
  );
}
