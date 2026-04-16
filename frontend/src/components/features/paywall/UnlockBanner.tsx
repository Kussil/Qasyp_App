"use client";
import { Button } from "@/components/ui/Button";

interface UnlockBannerProps {
  lockedCount: number;
  onUnlock: () => void;
}

export function UnlockBanner({ lockedCount, onUnlock }: UnlockBannerProps) {
  if (lockedCount === 0) return null;
  return (
    <div className="rounded-lg border border-primary-200 bg-primary-50 p-4 flex items-center justify-between">
      <span className="text-sm text-primary-800 font-medium">
        +{lockedCount} партнёров скрыто / Толық тізімді ашу
      </span>
      <Button size="sm" onClick={onUnlock}>
        Разблокировать список
      </Button>
    </div>
  );
}
