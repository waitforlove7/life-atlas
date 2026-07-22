export type PlaceStatus = 'visited' | 'wishlist' | 'lived' | 'worked' | 'studied';

export interface PlaceSummary {
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
