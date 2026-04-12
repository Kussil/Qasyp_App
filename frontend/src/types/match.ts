export interface MatchResult {
  profile_id: string | null;
  company_name: string;
  industry_sector?: string;
  operating_regions?: string[];
  match_score: number | null;
  explanation?: string;
  locked: boolean;
}

export interface MatchListResponse {
  matches: MatchResult[];
  total: number;
  has_more: boolean;
}
