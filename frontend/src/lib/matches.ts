import { api } from "@/lib/api";
import type { MatchListResponse } from "@/types/match";

export async function getMatches(limit = 20, offset = 0): Promise<MatchListResponse> {
  return api.get<MatchListResponse>(`/matches?limit=${limit}&offset=${offset}`);
}
