export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type PlaceStatus = 'visited' | 'wishlist' | 'lived' | 'worked' | 'studied';
export type ViewLevel = 'country' | 'province' | 'place';

export interface Place {
  id: string;
  name: string;
  longitude: number;
  latitude: number;
  status: PlaceStatus;
  country: string;
  country_iso: string;
  province: string;
  province_code: string;
}

export interface CountryStat {
  iso_code: string;
  name: string;
  visited: boolean;
}

export interface ProvinceStat {
  code: string;
  name: string;
  country_iso: string;
  visited: boolean;
}

export interface SelectedProvince {
  country: string;
  countryIso: string;
  province: string;
  provinceCode: string;
}

export interface Summary {
  countries_visited: number;
  provinces_visited: number;
  places_total: number;
}

export interface StatusBreakdown {
  status: string;
  count: number;
  percentage: number;
}

export interface TimelinePoint {
  month: string;
  count: number;
  cumulative: number;
}

export const STATUS_COLORS: Record<PlaceStatus, string> = {
  visited: '#22c55e',
  wishlist: '#eab308',
  lived: '#3b82f6',
  worked: '#8b5cf6',
  studied: '#f97316',
};

export const UNLIT_COLOR = '#d1d5db';
export const LIT_COLOR = '#60a5fa';

export async function getJson<T>(url: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url);
  } catch {
    throw new Error('API unavailable: ' + url);
  }
  if (!response.ok) throw new Error('Request failed (' + response.status + '): ' + url);
  return response.json() as Promise<T>;
}
