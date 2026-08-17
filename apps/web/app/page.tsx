'use client';

import { useCallback, useEffect, useState } from 'react';

import AddPlaceDialog from './components/AddPlaceDialog';
import PlaceDetailPanel from './components/PlaceDetailPanel';
import MapLegend from '../components/MapLegend';
import StatsPanel from '../components/StatsPanel';
import { useAtlasMap } from '../hooks/useAtlasMap';
import { API_URL, getJson, type Place, type StatusBreakdown, type Summary, type TimelinePoint } from '../lib/atlas';

const STATS_STORAGE_KEY = 'atlas-stats-open';

function readStoredStatsOpen(): boolean {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem(STATS_STORAGE_KEY) === 'true';
}

export default function Home() {
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [addingPlace, setAddingPlace] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [breakdown, setBreakdown] = useState<StatusBreakdown[]>([]);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [statsLoading, setStatsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelectPlace = useCallback((place: Place) => {
    setShowStats(false);
    setSelectedPlace(place);
  }, []);
  const handleError = useCallback((message: string) => setError(message), []);

  const { mapContainer, level, countryName, provinceName, selectedProvince, loading, showWorld, showProvince } =
    useAtlasMap({ onSelectPlace: handleSelectPlace, onError: handleError });

  const toggleStats = useCallback(() => {
    setSelectedPlace(null);
    setShowStats((prev) => {
      const next = !prev;
      localStorage.setItem(STATS_STORAGE_KEY, String(next));
      return next;
    });
  }, []);

  const loadStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const results = await Promise.all([
        getJson<Summary>(API_URL + '/stats/summary'),
        getJson<StatusBreakdown[]>(API_URL + '/stats/status-breakdown'),
        getJson<TimelinePoint[]>(API_URL + '/stats/timeline'),
      ]);
      setSummary(results[0]);
      setBreakdown(results[1]);
      setTimeline(results[2]);
    } catch (statsError) {
      setError(statsError instanceof Error ? statsError.message : 'Statistics are unavailable.');
    } finally {
      setStatsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Restore the persisted stats panel state only after mount to avoid hydration mismatch.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setShowStats(readStoredStatsOpen());
  }, []);

  useEffect(() => {
    if (showStats) {
      // Opening the panel loads stats, which sets state synchronously; intentional.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      void loadStats();
    }
  }, [showStats, loadStats]);

  return (
    <main className="atlas-shell">
      <div ref={mapContainer} id="map" />

      <div className="atlas-panel">
        <header className="atlas-header-row">
          <div>
            <h1>Atlas</h1>
          </div>
          <nav aria-label="Map level">
            <button onClick={showWorld} disabled={level === 'country'}>
              Countries
            </button>
            <span>/</span>
            <button onClick={showProvince} disabled={level === 'country' || level === 'province'}>
              {countryName || 'Provinces'}
            </button>
            {level === 'place' && (
              <>
                <span>/</span>
                <strong>{provinceName}</strong>
              </>
            )}
          </nav>
          <button className={showStats ? 'nav-active' : ''} onClick={toggleStats} style={{ fontWeight: 700 }}>
            Stats
          </button>
          <button className="add-place-button" onClick={() => setAddingPlace(true)}>
            + Add Place
          </button>
        </header>
        <StatsPanel open={showStats} loading={statsLoading} summary={summary} breakdown={breakdown} timeline={timeline} />
      </div>

      <aside className={'detail-content' + (selectedPlace ? ' detail-content-open' : '')} aria-label="Place details">
        {selectedPlace && (
          <PlaceDetailPanel
            placeId={selectedPlace.id}
            onClose={() => setSelectedPlace(null)}
            onDeleted={() => {
              setSelectedPlace(null);
              window.location.reload();
            }}
          />
        )}
      </aside>

      <MapLegend />

      {loading && <div className="map-message">Loading Atlas...</div>}
      {error && (
        <div className="map-message error" role="alert">
          {error}
        </div>
      )}

      {addingPlace && (
        <AddPlaceDialog
          initialSelection={selectedProvince}
          onClose={() => setAddingPlace(false)}
          onSaved={() => window.location.reload()}
        />
      )}
    </main>
  );
}
