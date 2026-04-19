"use client";
import { DashboardHeader } from "@/components/features/dashboard/DashboardHeader";
import { MatchResultsList } from "@/components/features/dashboard/MatchResultsList";
import { EmptyState } from "@/components/features/dashboard/EmptyState";
import { LoadingState } from "@/components/features/dashboard/LoadingState";
import { useMatches } from "@/hooks/useMatches";
import { api } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useRequireAuth";

export default function DashboardPage() {
  useRequireAuth();
  const { data, loading, error, refetch } = useMatches();

  async function handleUnlock() {
    try {
      await api.post("/demo/upgrade", {});
      await refetch();
    } catch (err) {
      console.error("Unlock failed:", err);
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <DashboardHeader />
      {loading && <LoadingState />}
      {error && (
        <div className="text-center py-8 text-red-600">
          <p>Ошибка загрузки: {error}</p>
          <button onClick={refetch} className="mt-2 text-sm text-sky-600 hover:underline">
            Попробовать снова
          </button>
        </div>
      )}
      {!loading && !error && data && data.matches.length === 0 && <EmptyState />}
      {!loading && !error && data && data.matches.length > 0 && (
        <MatchResultsList data={data} onUnlock={handleUnlock} />
      )}
    </div>
  );
}
