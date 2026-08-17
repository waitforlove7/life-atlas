'use client';

import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';

import {
  API_URL,
  LIT_COLOR,
  STATUS_COLORS,
  UNLIT_COLOR,
  getJson,
  type CountryStat,
  type Place,
  type ProvinceStat,
  type SelectedProvince,
  type ViewLevel,
} from '../lib/atlas';

interface UseAtlasMapOptions {
  onSelectPlace: (place: Place) => void;
  onError: (message: string) => void;
}

/**
 * Owns the MapLibre instance and the country -> province -> place drill-down
 * state. The returned mapContainer ref must be attached to the map's <div>,
 * and showWorld/showProvince back the breadcrumb navigation buttons.
 */
export function useAtlasMap({ onSelectPlace, onError }: UseAtlasMapOptions) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markers = useRef<maplibregl.Marker[]>([]);
  const showWorldRef = useRef<() => void>(() => undefined);
  const showProvinceRef = useRef<() => void>(() => undefined);

  const [level, setLevel] = useState<ViewLevel>('country');
  const [countryName, setCountryName] = useState('');
  const [provinceName, setProvinceName] = useState('');
  const [selectedProvince, setSelectedProvince] = useState<SelectedProvince | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const container = mapContainer.current;
    if (!container || map.current) return;
    let disposed = false;

    async function initialize() {
      let places: Place[] = [];
      let countryStats: CountryStat[] = [];
      let provinceStats: ProvinceStat[] = [];
      try {
        const all = await Promise.all([
          getJson<Place[]>(API_URL + '/places'),
          getJson<CountryStat[]>(API_URL + '/stats/countries'),
          getJson<ProvinceStat[]>(API_URL + '/stats/provinces'),
        ]);
        places = all[0];
        countryStats = all[1];
        provinceStats = all[2];
      } catch {
        onError('Personal data is unavailable. The map is shown in offline mode.');
      }

      if (disposed || !container) return;

      const visitedCountries = countryStats
        .filter((item) => item.visited)
        .map((item) => item.iso_code);
      const visitedProvinces = new Set(
        provinceStats
          .filter((item) => item.visited)
          .map((item) => item.country_iso + ':' + item.code),
      );
      let selectedCountryIso = '';
      let selectedCountryName = '';

      const instance = new maplibregl.Map({
        container,
        style: {
          version: 8,
          sources: {},
          layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#f8fafc' } }],
        } as maplibregl.StyleSpecification,
        center: [20, 20],
        zoom: 1.5,
        attributionControl: false,
      });
      map.current = instance;
      instance.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

      const clearMarkers = () => {
        markers.current.forEach((marker) => marker.remove());
        markers.current = [];
      };
      const setVisibility = (layers: string[], visible: boolean) => {
        layers.forEach((layer) => {
          if (instance.getLayer(layer)) {
            instance.setLayoutProperty(layer, 'visibility', visible ? 'visible' : 'none');
          }
        });
      };

      const showWorld = () => {
        clearMarkers();
        setVisibility(['provinces-fill', 'provinces-outline'], false);
        setVisibility(['countries-fill', 'countries-outline'], true);
        instance.flyTo({ center: [20, 20], zoom: 1.5 });
        setLevel('country');
        setCountryName('');
        setProvinceName('');
        setSelectedProvince(null);
      };
      const showProvince = () => {
        clearMarkers();
        setVisibility(['countries-fill', 'countries-outline'], false);
        setVisibility(['provinces-fill', 'provinces-outline'], true);
        setLevel('province');
        setProvinceName('');
        setSelectedProvince(null);
      };
      showWorldRef.current = showWorld;
      showProvinceRef.current = showProvince;

      const boundsFor = (features: GeoJSON.Feature[]): maplibregl.LngLatBounds => {
        const bounds = new maplibregl.LngLatBounds();
        const visit = (coordinates: unknown) => {
          if (Array.isArray(coordinates) && typeof coordinates[0] === 'number') {
            bounds.extend(coordinates as [number, number]);
          } else if (Array.isArray(coordinates)) {
            coordinates.forEach(visit);
          }
        };
        features.forEach((feature) => {
          if (feature.geometry && 'coordinates' in feature.geometry) {
            visit(feature.geometry.coordinates);
          }
        });
        return bounds;
      };

      const showPlaces = (provinceCode: string, name: string, bounds: maplibregl.LngLatBounds) => {
        clearMarkers();
        setLevel('place');
        setProvinceName(name);
        setSelectedProvince({
          country: selectedCountryName,
          countryIso: selectedCountryIso,
          province: name,
          provinceCode,
        });
        places
          .filter((place) => place.country_iso === selectedCountryIso && place.province_code === provinceCode)
          .forEach((place) => {
            const element = document.createElement('button');
            element.className = 'place-marker';
            element.style.backgroundColor = STATUS_COLORS[place.status];
            element.setAttribute('aria-label', place.name);
            element.title = place.name + ' (' + place.province + ', ' + place.country + ')';
            element.onclick = (event) => {
              event.stopPropagation();
              onSelectPlace(place);
            };
            markers.current.push(
              new maplibregl.Marker({ element }).setLngLat([place.longitude, place.latitude]).addTo(instance),
            );
          });
        if (!bounds.isEmpty()) instance.fitBounds(bounds, { padding: 64, maxZoom: 11 });
      };

      const showCountry = async (isoCode: string, name: string) => {
        const data = await getJson<GeoJSON.FeatureCollection>('/data/admin1/' + isoCode + '.geojson');
        data.features.forEach((feature) => {
          if (feature.properties) {
            feature.properties.visited = visitedProvinces.has(
              isoCode + ':' + String(feature.properties.code || ''),
            );
          }
        });
        const source = instance.getSource('provinces') as maplibregl.GeoJSONSource | undefined;
        if (source) {
          source.setData(data);
        } else {
          instance.addSource('provinces', { type: 'geojson', data });
          instance.addLayer({
            id: 'provinces-fill',
            type: 'fill',
            source: 'provinces',
            paint: {
              'fill-color': ['case', ['boolean', ['get', 'visited'], false], LIT_COLOR, UNLIT_COLOR],
              'fill-opacity': 0.72,
            },
          } as maplibregl.LayerSpecification);
          instance.addLayer({
            id: 'provinces-outline',
            type: 'line',
            source: 'provinces',
            paint: { 'line-color': '#ffffff', 'line-width': 1 },
          } as maplibregl.LayerSpecification);
        }
        selectedCountryIso = isoCode;
        selectedCountryName = name;
        setCountryName(name);
        showProvince();
        const bounds = boundsFor(data.features);
        if (!bounds.isEmpty()) instance.fitBounds(bounds, { padding: 48, maxZoom: 6 });
      };

      instance.once('load', () => {
        instance.addSource('countries', { type: 'geojson', data: '/data/countries.geojson' });
        instance.addLayer({
          id: 'countries-fill',
          type: 'fill',
          source: 'countries',
          paint: {
            'fill-color': ['case', ['in', ['get', 'iso_code'], ['literal', visitedCountries]], LIT_COLOR, UNLIT_COLOR],
            'fill-opacity': 0.76,
          },
        } as maplibregl.LayerSpecification);
        instance.addLayer({
          id: 'countries-outline',
          type: 'line',
          source: 'countries',
          paint: { 'line-color': '#ffffff', 'line-width': 0.8 },
        } as maplibregl.LayerSpecification);
        instance.on('click', 'countries-fill', async (event: maplibregl.MapLayerMouseEvent) => {
          const props = event.features?.[0]?.properties;
          if (!props?.iso_code) return;
          try {
            await showCountry(String(props.iso_code), String(props.name || props.iso_code));
          } catch {
            onError('No first-level boundary data is available for ' + (props.name || props.iso_code) + '.');
          }
        });
        instance.on('click', 'provinces-fill', (event: maplibregl.MapLayerMouseEvent) => {
          const feature = event.features?.[0];
          if (!feature?.properties?.code) return;
          showPlaces(String(feature.properties.code), String(feature.properties.name), boundsFor([feature]));
        });
        ['countries-fill', 'provinces-fill'].forEach((layer) => {
          instance.on('mouseenter', layer, () => {
            instance.getCanvas().style.cursor = 'pointer';
          });
          instance.on('mouseleave', layer, () => {
            instance.getCanvas().style.cursor = '';
          });
        });
        setLoading(false);
      });
    }

    void initialize();
    return () => {
      disposed = true;
      map.current?.remove();
      map.current = null;
    };
  }, [onSelectPlace, onError]);

  return {
    mapContainer,
    level,
    countryName,
    provinceName,
    selectedProvince,
    loading,
    showWorld: () => showWorldRef.current(),
    showProvince: () => showProvinceRef.current(),
  };
}
