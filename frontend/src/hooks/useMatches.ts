"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { MatchListResponse } from "@/types/match";

export function useMatches() {
  const [data, setData] = useState<MatchListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function fetchMatches() {
    setLoading(true);
    setError(null);
    try {
      const result = await api.get<MatchListResponse>("/matches?limit=20");
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load matches");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchMatches();
  }, []);

  return { data, loading, error, refetch: fetchMatches };
}
