import { Badge } from "@/components/ui/Badge";
import { MatchScoreBadge } from "./MatchScoreBadge";
import type { MatchResult } from "@/types/match";

interface MatchCardProps {
  match: MatchResult;
}

export function MatchCard({ match }: MatchCardProps) {
  if (match.locked) {
    return (
      <div className="rounded-lg bg-white border border-gray-200 p-4 relative overflow-hidden min-h-[140px]">
        <div className="filter blur-sm space-y-2">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          <div className="h-3 bg-gray-200 rounded w-2/3"></div>
        </div>
        <div className="absolute inset-0 flex items-center justify-center bg-white/70">
          <div className="text-center">
            <div className="text-3xl mb-1">🔒</div>
            <span className="text-xs text-gray-500 font-medium">Заблокировано</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-white border border-gray-200 p-4 shadow-sm flex flex-col gap-3">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-semibold text-gray-900 truncate">{match.company_name}</h3>
          {match.industry_sector && (
            <Badge variant="teal" className="mt-1">{match.industry_sector}</Badge>
          )}
        </div>
        <div className="ml-3 flex-shrink-0">
          <MatchScoreBadge score={match.match_score} />
        </div>
      </div>
      {match.operating_regions && match.operating_regions.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {match.operating_regions.slice(0, 3).map((r) => (
            <Badge key={r} variant="default" className="text-xs">{r}</Badge>
          ))}
        </div>
      )}
      {match.explanation && (
        <p className="text-sm text-gray-500 line-clamp-2">{match.explanation}</p>
      )}
      <button className="text-sm text-primary-600 hover:underline text-left mt-auto">
        Подробнее →
      </button>
    </div>
  );
}
