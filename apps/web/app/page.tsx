/* eslint-disable @typescript-eslint/ban-ts-comment */
﻿// @ts-nocheck
﻿'use client';



// @ts-nocheck
/* eslint-disable react-hooks/set-state-in-effect */
import React, { useCallback, useEffect, useRef, useState } from 'react';

import maplibregl from 'maplibre-gl';

import AddPlaceDialog from './components/AddPlaceDialog';
import PlaceDetailPanel from './components/PlaceDetailPanel';



const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const UNLIT_COLOR = '#d1d5db';

const LIT_COLOR = '#60a5fa';

const STATS_STORAGE_KEY = 'atlas-stats-open';

type ViewLevel = 'country' | 'province' | 'place';

type PlaceStatus = 'visited' | 'wishlist' | 'lived' | 'worked' | 'studied';

interface Place { id: string; name: string; longitude: number; latitude: number; status: PlaceStatus; country: string; country_iso: string; province: string; province_code: string; }

interface CountryStat { iso_code: string; name: string; visited: boolean; }

interface ProvinceStat { code: string; name: string; country_iso: string; visited: boolean; }

interface SelectedProvince { country: string; countryIso: string; province: string; provinceCode: string; }

interface Summary { countries_visited: number; provinces_visited: number; places_total: number; }

interface StatusBreakdown { status: string; count: number; percentage: number; }

interface TimelinePoint { month: string; count: number; cumulative: number; }


const STATUS_COLORS: Record<PlaceStatus, string> = { visited: '#22c55e', wishlist: '#eab308', lived: '#3b82f6', worked: '#8b5cf6', studied: '#f97316' };

const ST_COLORS: Record<string, string> = { visited: '#22c55e', wishlist: '#eab308', lived: '#3b82f6', worked: '#8b5cf6', studied: '#f97316' };

async function getJson<T>(url: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url);
  } catch {
    throw new Error('API unavailable: ' + url);
  }
  if (!response.ok) throw new Error('Request failed (' + response.status + '): ' + url);
  return response.json() as Promise<T>;
}

function formatMonth(monthStr: string): string { const parts = monthStr.split('-'); return parts[0] + '-' + parts[1]; }

function readStoredStatsOpen(): boolean { if (typeof window === 'undefined') return false; return localStorage.getItem(STATS_STORAGE_KEY) === 'true'; }







export default function Home() {

  const mapContainer = useRef<HTMLDivElement>(null); const map = useRef<maplibregl.Map | null>(null); const markers = useRef<maplibregl.Marker[]>([]); const showWorldRef = useRef<() => void>(() => undefined); const showProvinceRef = useRef<() => void>(() => undefined);

  const [level, setLevel] = useState<ViewLevel>('country'); const [countryName, setCountryName] = useState(''); const [provinceName, setProvinceName] = useState(''); const [selectedProvince, setSelectedProvince] = useState<SelectedProvince | null>(null); const [selectedPlace, setSelectedPlace] = useState<Place | null>(null); const [addingPlace, setAddingPlace] = useState(false); const [loading, setLoading] = useState(true); const [error, setError] = useState<string | null>(null);

  const [showStats, setShowStats] = useState(false); const [summary, setSummary] = useState<Summary | null>(null); const [breakdown, setBreakdown] = useState<StatusBreakdown[]>([]); const [timeline, setTimeline] = useState<TimelinePoint[]>([]); const [statsLoading, setStatsLoading] = useState(false);



  const toggleStats = useCallback(function() { setSelectedPlace(null); setShowStats(function(prev) { const next = !prev; localStorage.setItem(STATS_STORAGE_KEY, String(next)); return next; }); }, []);



  const loadStats = useCallback(async function() {

    setStatsLoading(true);

    try {

      const results = await Promise.all([

        getJson<Summary>(API_URL + '/stats/summary'),

        getJson<StatusBreakdown[]>(API_URL + '/stats/status-breakdown'),

        getJson<TimelinePoint[]>(API_URL + '/stats/timeline'),


      ]);

      setSummary(results[0]); setBreakdown(results[1]); setTimeline(results[2]);

    } catch (statsError) {
      setError(statsError instanceof Error ? statsError.message : 'Statistics are unavailable.');
    } finally { setStatsLoading(false); }

  }, []);



  useEffect(function() { setShowStats(readStoredStatsOpen()); }, []);



  useEffect(function() {

    if (!mapContainer.current || map.current) return; let disposed = false;

    async function initialize() {

      let places: Place[] = []; let countryStats: CountryStat[] = []; let provinceStats: ProvinceStat[] = [];

      try { const all = await Promise.all([getJson<Place[]>(API_URL + '/places'), getJson<CountryStat[]>(API_URL + '/stats/countries'), getJson<ProvinceStat[]>(API_URL + '/stats/provinces')]); places = all[0]; countryStats = all[1]; provinceStats = all[2]; } catch { setError('Personal data is unavailable. The map is shown in offline mode.'); }

      if (disposed || !mapContainer.current) return;

      const visitedCountries = countryStats.filter(function(item) { return item.visited; }).map(function(item) { return item.iso_code; }); const visitedProvinces = new Set(provinceStats.filter(function(item) { return item.visited; }).map(function(item) { return item.country_iso + ':' + item.code; })); let selectedCountryIso = ''; let selectedCountryName = '';

      const instance = new maplibregl.Map({ container: mapContainer.current, style: { version: 8, sources: {}, layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#f8fafc' } }] }, center: [20, 20], zoom: 1.5, attributionControl: false }); map.current = instance; instance.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

      const clearMarkers = function() { markers.current.forEach(function(marker) { marker.remove(); }); markers.current = []; }; const visibility = function(layers: string[], visible: boolean) { layers.forEach(function(layer) { if (instance.getLayer(layer)) instance.setLayoutProperty(layer, 'visibility', visible ? 'visible' : 'none'); }); };

      const showWorld = function() { clearMarkers(); visibility(['provinces-fill', 'provinces-outline'], false); visibility(['countries-fill', 'countries-outline'], true); instance.flyTo({ center: [20, 20], zoom: 1.5 }); setLevel('country'); setCountryName(''); setProvinceName(''); setSelectedProvince(null); setSelectedPlace(null); };

      const showProvince = function() { clearMarkers(); visibility(['countries-fill', 'countries-outline'], false); visibility(['provinces-fill', 'provinces-outline'], true); setLevel('province'); setProvinceName(''); setSelectedProvince(null); setSelectedPlace(null); }; showWorldRef.current = showWorld; showProvinceRef.current = showProvince;

      const boundsFor = function(features: GeoJSON.Feature[]) { const bounds = new maplibregl.LngLatBounds(); const visit = function(coordinates: unknown) { if (Array.isArray(coordinates) && typeof coordinates[0] === 'number') bounds.extend(coordinates as [number, number]); else if (Array.isArray(coordinates)) coordinates.forEach(visit); }; features.forEach(function(feature) { if (feature.geometry && 'coordinates' in feature.geometry) visit(feature.geometry.coordinates); }); return bounds; };

      const showPlaces = function(provinceCode: string, name: string, bounds: maplibregl.LngLatBounds) { clearMarkers(); setLevel('place'); setProvinceName(name); setSelectedProvince({ country: selectedCountryName, countryIso: selectedCountryIso, province: name, provinceCode: provinceCode }); places.filter(function(place) { return place.country_iso === selectedCountryIso && place.province_code === provinceCode; }).forEach(function(place) { const element = document.createElement('button'); element.className = 'place-marker'; element.style.backgroundColor = STATUS_COLORS[place.status]; element.setAttribute('aria-label', place.name); element.title = place.name + ' (' + place.province + ', ' + place.country + ')'; element.onclick = function(e) { e.stopPropagation(); setShowStats(false); setSelectedPlace(place); }; markers.current.push(new maplibregl.Marker({ element: element }).setLngLat([place.longitude, place.latitude]).addTo(instance)); }); if (!bounds.isEmpty()) instance.fitBounds(bounds, { padding: 64, maxZoom: 11 }); };

      const showCountry = async function(isoCode, name) { const data = await getJson<GeoJSON.FeatureCollection>('/data/admin1/' + isoCode + '.geojson'); data.features.forEach(function(feature) { if (feature.properties) feature.properties.visited = visitedProvinces.has(isoCode + ':' + String(feature.properties.code || '')); }); const source = instance.getSource('provinces'); if (source) source.setData(data); else { instance.addSource('provinces', { type: 'geojson', data: data }); instance.addLayer({ id: 'provinces-fill', type: 'fill', source: 'provinces', paint: { 'fill-color': ['case', ['boolean', ['get', 'visited'], false], LIT_COLOR, UNLIT_COLOR], 'fill-opacity': 0.72 } }); instance.addLayer({ id: 'provinces-outline', type: 'line', source: 'provinces', paint: { 'line-color': '#ffffff', 'line-width': 1 } }); } selectedCountryIso = isoCode; selectedCountryName = name; setCountryName(name); showProvince(); const bounds = boundsFor(data.features); if (!bounds.isEmpty()) instance.fitBounds(bounds, { padding: 48, maxZoom: 6 }); };

      instance.once('load', function() { instance.addSource('countries', { type: 'geojson', data: '/data/countries.geojson' }); instance.addLayer({ id: 'countries-fill', type: 'fill', source: 'countries', paint: { 'fill-color': ['case', ['in', ['get', 'iso_code'], ['literal', visitedCountries]], LIT_COLOR, UNLIT_COLOR], 'fill-opacity': 0.76 } }); instance.addLayer({ id: 'countries-outline', type: 'line', source: 'countries', paint: { 'line-color': '#ffffff', 'line-width': 0.8 } }); instance.on('click', 'countries-fill', async function(event) { const props = event.features?.[0]?.properties; if (!props?.iso_code) return; try { await showCountry(String(props.iso_code), String(props.name || props.iso_code)); } catch { setError('No first-level boundary data is available for ' + (props.name || props.iso_code) + '.'); } }); instance.on('click', 'provinces-fill', function(event) { const feature = event.features?.[0]; if (!feature?.properties?.code) return; showPlaces(String(feature.properties.code), String(feature.properties.name), boundsFor([feature])); }); ['countries-fill', 'provinces-fill'].forEach(function(layer) { instance.on('mouseenter', layer, function() { instance.getCanvas().style.cursor = 'pointer'; }); instance.on('mouseleave', layer, function() { instance.getCanvas().style.cursor = ''; }); }); setLoading(false); });

    }

    void initialize(); return function() { disposed = true; map.current?.remove(); map.current = null; };

  }, []);



  useEffect(function() { if (showStats) { void loadStats(); } }, [showStats, loadStats]);



  const maxTimelineCount = Math.max.apply(null, timeline.map(function(p) { return p.count; }).concat([1]));

  const maxCumulative = Math.max.apply(null, timeline.map(function(p) { return p.cumulative; }).concat([1]));




  return React.createElement('main', { className: 'atlas-shell' },

    React.createElement('div', { ref: mapContainer, id: 'map' }),

    React.createElement('div', { className: 'atlas-panel' },

      React.createElement('header', { className: 'atlas-header-row' },

        React.createElement('div', null,

          React.createElement('h1', null, 'Atlas'),


        ),

        React.createElement('nav', { 'aria-label': 'Map level' },

          React.createElement('button', { onClick: function() { showWorldRef.current(); }, disabled: level === 'country' }, 'Countries'),

          React.createElement('span', null, '/'),

          React.createElement('button', { onClick: function() { showProvinceRef.current(); }, disabled: level === 'country' || level === 'province' }, countryName || 'Provinces'),

          level === 'place' && React.createElement(React.Fragment, null,

            React.createElement('span', null, '/'),

            React.createElement('strong', null, provinceName)

          )

        ),

        React.createElement('button', { className: showStats ? 'nav-active' : '', onClick: toggleStats, style: { fontWeight: 700 } }, 'Stats'),

        React.createElement('button', { className: 'add-place-button', onClick: function() { setAddingPlace(true); } }, '+ Add Place')

      ),

      React.createElement('aside', { className: 'stats-content' + (showStats ? ' stats-content-open' : ''), 'aria-label': 'Statistics', 'aria-expanded': showStats },

      statsLoading ? React.createElement('p', { className: 'stats-content-loading' }, 'Loading stats...') :

      summary ? React.createElement(React.Fragment, null,

        React.createElement('section', { className: 'stats-summary' },

          React.createElement('div', { className: 'stat-card' },

            React.createElement('span', { className: 'stat-value' }, summary.countries_visited),

            React.createElement('span', { className: 'stat-label' }, 'Countries visited')

          ),

          React.createElement('div', { className: 'stat-card' },

            React.createElement('span', { className: 'stat-value' }, summary.provinces_visited),

            React.createElement('span', { className: 'stat-label' }, 'Provinces visited')

          ),

          React.createElement('div', { className: 'stat-card' },

            React.createElement('span', { className: 'stat-value' }, summary.places_total),

            React.createElement('span', { className: 'stat-label' }, 'Total places')

          )

        ),

        React.createElement('section', { className: 'stats-section' },

          React.createElement('h2', null, 'Status breakdown'),

          React.createElement('div', { className: 'status-bars' },

            breakdown.map(function(item) { return React.createElement('div', { key: item.status, className: 'status-bar-row' },

              React.createElement('span', { className: 'status-bar-label', style: { color: ST_COLORS[item.status] || '#64748b' } }, item.status),

              React.createElement('div', { className: 'status-bar-track' },

                React.createElement('div', { className: 'status-bar-fill', style: { width: Math.max(item.percentage, 2) + '%', backgroundColor: ST_COLORS[item.status] || '#64748b' } })

              ),

              React.createElement('span', { className: 'status-bar-count' }, item.count)

            ); })

          )

        ),

        timeline.length > 0 && React.createElement('section', { className: 'stats-section' },

          React.createElement('h2', null, 'Timeline'),

          React.createElement('div', { className: 'timeline-chart' },

            React.createElement('div', { className: 'timeline-bars' },

              timeline.map(function(point) { return React.createElement('div', { key: point.month, className: 'timeline-column' },

                React.createElement('div', { className: 'timeline-bar-wrapper' },

                React.createElement('div', { className: 'timeline-bar', style: { height: (point.count / maxTimelineCount * 100) + '%' }, title: formatMonth(point.month) + ': ' + point.count + ' visit(s)' })

                ),

                React.createElement('span', { className: 'timeline-label' }, formatMonth(point.month))

              ); })

            ),

            React.createElement('div', { className: 'timeline-cumulative' },

              React.createElement('span', { className: 'timeline-cumulative-label' }, 'Cumulative'),

              React.createElement('div', { className: 'timeline-cumulative-track' },

                React.createElement('svg', { viewBox: '0 0 ' + (timeline.length * 40) + ' 100', preserveAspectRatio: 'none' },

                  React.createElement('polyline', { fill: 'none', stroke: '#2563eb', strokeWidth: '2', points: timeline.map(function(p, i) { return (i * 40 + 20) + ',' + (100 - (p.cumulative / maxCumulative) * 90); }).join(' ') })

                )

              )

            )

          )

        ),


      ) : null

    ),

  React.createElement('aside', { className: 'detail-content' + (selectedPlace ? ' detail-content-open' : ''), 'aria-label': 'Place details' },
    selectedPlace && React.createElement(PlaceDetailPanel, { placeId: selectedPlace.id, onClose: function() { setSelectedPlace(null); }, onDeleted: function() { setSelectedPlace(null); window.location.reload(); } })
  )

  ),

  React.createElement('aside', { className: 'map-legend' },

      React.createElement('span', null, React.createElement('i', { className: 'legend-swatch unlit' }), 'Not visited'),

      React.createElement('span', null, React.createElement('i', { className: 'legend-swatch lit' }), 'Visited')

    ),

  loading && React.createElement('div', { className: 'map-message' }, 'Loading Atlas...'),

  error && React.createElement('div', { className: 'map-message error', role: 'alert' }, error),

  addingPlace && React.createElement(AddPlaceDialog, { initialSelection: selectedProvince, onClose: function() { setAddingPlace(false); }, onSaved: function() { window.location.reload(); } })

  );

}
