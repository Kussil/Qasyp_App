export type LegalEntityType = "TOO" | "IP" | "AO" | "GP" | "OTHER";
export type Frequency = "ONE_TIME" | "WEEKLY" | "MONTHLY" | "QUARTERLY" | "ANNUAL";
export type RevenueRange =
  | "BELOW_10M"
  | "10M_50M"
  | "50M_200M"
  | "200M_1B"
  | "ABOVE_1B"
  | "PREFER_NOT_TO_SAY";
export type Region =
  | "ALMATY_CITY" | "ASTANA_CITY" | "SHYMKENT_CITY" | "ALMATY_REGION"
  | "AKMOLA" | "AKTOBE" | "ATYRAU" | "EAST_KZ" | "ZHAMBYL" | "WEST_KZ"
  | "KARAGANDA" | "KOSTANAY" | "KYZYLORDA" | "MANGYSTAU" | "PAVLODAR"
  | "NORTH_KZ" | "TURKESTAN" | "ABAI" | "ZHETYSU" | "ULYTAU";

export interface BusinessProfile {
  id: string;
  user_id: string;
  company_name: string;
  bin: string;
  legal_entity_type: LegalEntityType;
  vat_registered: boolean;
  vat_certificate_number?: string;
  industry_sector: string;
  business_scope: string;
  role: "BUYER" | "SUPPLIER" | "BOTH";
  products_services?: string[];
  volume_requirements?: string;
  frequency?: Frequency;
  quality_standards?: string[];
  delivery_requirements?: string;
  annual_revenue_range?: RevenueRange;
  growth_target?: string;
  operating_regions?: Region[];
  willing_cross_border?: boolean;
  preferred_partner_profile?: string;
  exclusion_criteria?: string;
  embedding_generated: boolean;
}
