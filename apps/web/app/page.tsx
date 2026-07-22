'use client';

import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

interface Place {
  id: string; name: string; longitude: number; latitude: number;
  status: string; favorite: boolean; country: string; city: string;
}

interface CountryStat {
  iso_code: string; name: string; visited: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  visited: '#22c55e', wishlist: '#eab308', lived: '#3b82f6',
  worked: '#8b5cf6', studied: '#f97316',
};

export default function Home() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const [places, setPlaces] = useState<Place[]>([]);
  const [visitedCountries, setVisitedCountries] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(API_URL + '/places').then(r => r.json()),
      fetch(API_URL + '/stats/countries').then(r => r.json()),
    ]).then(([placesData, countriesData]) => {
      setPlaces(placesData);
      setVisitedCountries(new Set(
        (countriesData as CountryStat[]).filter(c => c.visited).map(c => c.iso_code)
      ));
      setLoading(false);
    }).catch(err => {
      console.error('Failed to fetch data:', err);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://demotiles.maplibre.org/style.json',
      center: [30, 20],
      zoom: 2,
    });
    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');

    map.current.once('load', () => {
      if (!map.current) return;

      // --- Country fill layer ---
      map.current.addSource('countries', {
        type: 'geojson',
        data: '/data/countries.geojson',
      });

      map.current.addLayer({
        id: 'countries-fill',
        type: 'fill',
        source: 'countries',
        paint: {
          'fill-color': [
            'case',
            ['in', ['get', 'ISO_A3'], ['literal', Array.from(visitedCountries)]],
            '#dbeafe',
            '#e5e7eb'
          ],
          'fill-opacity': 0.7,
        },
      });

      map.current.addLayer({
        id: 'countries-outline',
        type: 'line',
        source: 'countries',
        paint: {
          'line-color': '#9ca3af',
          'line-width': 0.5,
        },
      });

      // Click on country
      map.current.on('click', 'countries-fill', (e) => {
        if (!e.features?.length || !map.current) return;
        const props = e.features[0].properties as Record<string, unknown>;
        const name = props.ADMIN as string;
        const iso = props.ISO_A3 as string;
        const visited = visitedCountries.has(iso);
        new maplibregl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(
            '<strong>' + name + '</strong><br/>' +
            '<span style="font-size:12px;color:' + (visited ? '#22c55e' : '#9ca3af') + '">' +
            (visited ? 'Visited' : 'Not visited') + '</span>'
          )
          .addTo(map.current);
      });

      map.current.on('mouseenter', 'countries-fill', () => {
        if (map.current) map.current.getCanvas().style.cursor = 'pointer';
      });
      map.current.on('mouseleave', 'countries-fill', () => {
        if (map.current) map.current.getCanvas().style.cursor = '';
      });
    });

    return () => { map.current?.remove(); map.current = null; };
  }, []);

  // Update country fill when visitedCountries changes
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;
    const arr = Array.from(visitedCountries);
    (map.current as maplibregl.Map).setPaintProperty('countries-fill', 'fill-color', [
      'case',
      ['in', ['get', 'ISO_A3'], ['literal', arr]],
      '#dbeafe',
      '#e5e7eb'
    ]);
  }, [visitedCountries]);

  // Place markers
  useEffect(() => {
    if (!map.current || !places.length) return;
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    places.forEach(place => {
      const color = STATUS_COLORS[place.status] || '#6b7280';
      const el = document.createElement('div');
      el.style.cssText = 'background:' + color + ';width:14px;height:14px;border-radius:50%;border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.4);cursor:pointer;transform:translate(-50%,-50%);';

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([place.longitude, place.latitude])
        .setPopup(new maplibregl.Popup({ offset: 16 }).setHTML(
          '<div style="font-family:system-ui,sans-serif;font-size:13px;line-height:1.5;min-width:140px">' +
          '<strong>' + place.name + '</strong><br/>' +
          '<span style="color:#6b7280">' + place.city + ', ' + place.country + '</span><br/>' +
          '<span style="display:inline-block;background:' + color + ';color:white;padding:1px 6px;border-radius:3px;font-size:11px;margin-top:4px">' +
          place.status + (place.favorite ? ' ★' : '') + '</span></div>'
        ))
        .addTo(map.current!);
      markersRef.current.push(marker);
    });

    if (places.length > 0 && map.current) {
      const bounds = new maplibregl.LngLatBounds();
      places.forEach(p => bounds.extend([p.longitude, p.latitude]));
      map.current.fitBounds(bounds, { padding: 60, maxZoom: 12 });
    }
  }, [places]);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      <div ref={mapContainer} id="map" />
      {loading && (
        <div style={{ position: 'absolute', top: 16, left: 16, background: 'white',
          padding: '8px 16px', borderRadius: 8, boxShadow: '0 1px 4px rgba(0,0,0,0.15)',
          fontSize: 14, fontFamily: 'system-ui, sans-serif' }}>
          Loading...
        </div>
      )}
    </div>
  );
}
