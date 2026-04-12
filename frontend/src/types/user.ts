export type Role = "BUYER" | "SUPPLIER" | "BOTH";
export type Tier = "free" | "basic" | "pro";

export interface User {
  id: string;
  email: string;
  role: Role | null;
  tier: Tier;
  is_active: boolean;
}
