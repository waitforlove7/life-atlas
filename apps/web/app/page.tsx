'use client';

import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

interface Place {
  id: string;
  name: string;
  longitude: number;
  latitude: number;
  status: string;
  favorite: boolean;
  country: string;
  city: string;
}

const STATUS_COLORS: Record<string, string> = {
  visited: '#22c55e',
  wishlist: '#eab308',
  lived: '#3b82f6',
  worked: '#8b5cf6',
  studied: '#f97316',
};

export default function Home() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const [places, setPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(API_URL + '/places')
      .then((res) => res.json())
      .then((data) => {
        setPlaces(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch places:', err);
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
    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  useEffect(() => {
    if (!map.current || !places.length) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    places.forEach((place) => {
      const color = STATUS_COLORS[place.status] || '#6b7280';
      const el = document.createElement('div');
      el.className = 'marker';
      el.style.cssText =
        `background:${color};width:14px;height:14px;border-radius:50%;border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.4);cursor:pointer;transform:translate(-50%,-50%)`;

      const popup = new maplibregl.Popup({ offset: 16 }).setHTML(
        '<div style="font-family:system-ui,sans-serif;font-size:13px;line-height:1.5;min-width:140px">' +
          '<strong>' + place.name + '</strong><br/>' +
          '<span style="color:#6b7280">' + place.city + ', ' + place.country + '</span><br/>' +
          '<span style="display:inline-block;background:' + color + ';color:white;padding:1px 6px;border-radius:3px;font-size:11px;margin-top:4px">' +
          place.status + (place.favorite ? ' ?' : '') + '</span></div>'
      );

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([place.longitude, place.latitude])
        .setPopup(popup)
        .addTo(map.current!);
      markersRef.current.push(marker);
    });

    if (places.length > 0 && map.current) {
      const bounds = new maplibregl.LngLatBounds();
      places.forEach((p) => bounds.extend([p.longitude, p.latitude]));
      map.current.fitBounds(bounds, { padding: 60, maxZoom: 12 });
    }
  }, [places]);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      <div ref={mapContainer} id="map" />
      {loading && (
        <div
          style={{
            position: 'absolute',
            top: 16,
            left: 16,
            background: 'white',
            padding: '8px 16px',
            borderRadius: 8,
            boxShadow: '0 1px 4px rgba(0,0,0,0.15)',
            fontSize: 14,
            fontFamily: 'system-ui, sans-serif',
          }}
        >
          Loading places...
        </div>
      )}
    </div>
  );
}
