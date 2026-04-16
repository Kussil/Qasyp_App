"use client";
import { MatchCard } from "./MatchCard";
import type { MatchListResponse } from "@/types/match";

interface MatchResultsListProps {
  data: MatchListResponse;
  onUnlock: () => void;
}

export function MatchResultsList({ data, onUnlock }: MatchResultsListProps) {
  const lockedCount = data.matches.filter((m) => m.locked).length;

  return (
    <div className="space-y-4">
      {lockedCount > 0 && (
        <div className="rounded-lg border border-sky-200 bg-sky-50 p-4 flex items-center justify-between">
          <span className="text-sm text-sky-800 font-medium">
            +{lockedCount} партнёров скрыто
          </span>
          <button
            onClick={onUnlock}
            className="px-4 py-2 bg-sky-600 text-white rounded-md text-sm font-medium hover:bg-sky-700"
          >
            Разблокировать список
          </button>
        </div>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.matches.map((match, idx) => (
          <MatchCard key={match.profile_id ?? `locked-${idx}`} match={match} />
        ))}
      </div>
      <p className="text-sm text-gray-400 text-right">{data.total} партнёров найдено</p>
    </div>
  );
}
