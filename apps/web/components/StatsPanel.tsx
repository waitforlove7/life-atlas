'use client';

import {
  STATUS_COLORS,
  type PlaceStatus,
  type StatusBreakdown,
  type Summary,
  type TimelinePoint,
} from '../lib/atlas';

interface StatsPanelProps {
  open: boolean;
  loading: boolean;
  summary: Summary | null;
  breakdown: StatusBreakdown[];
  timeline: TimelinePoint[];
}

export default function StatsPanel({ open, loading, summary, breakdown, timeline }: StatsPanelProps) {
  const maxTimelineCount = Math.max(...timeline.map((point) => point.count), 1);
  const maxCumulative = Math.max(...timeline.map((point) => point.cumulative), 1);

  return (
    <aside className={'stats-content' + (open ? ' stats-content-open' : '')} aria-label="Statistics">
      {loading ? (
        <p className="stats-content-loading">Loading stats...</p>
      ) : summary ? (
        <>
          <section className="stats-summary">
            <div className="stat-card">
              <span className="stat-value">{summary.countries_visited}</span>
              <span className="stat-label">Countries visited</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{summary.provinces_visited}</span>
              <span className="stat-label">Provinces visited</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{summary.places_total}</span>
              <span className="stat-label">Total places</span>
            </div>
          </section>

          <section className="stats-section">
            <h2>Status breakdown</h2>
            <div className="status-bars">
              {breakdown.map((item) => (
                <div key={item.status} className="status-bar-row">
                  <span
                    className="status-bar-label"
                    style={{ color: STATUS_COLORS[item.status as PlaceStatus] ?? '#64748b' }}
                  >
                    {item.status}
                  </span>
                  <div className="status-bar-track">
                    <div
                      className="status-bar-fill"
                      style={{
                        width: Math.max(item.percentage, 2) + '%',
                        backgroundColor: STATUS_COLORS[item.status as PlaceStatus] ?? '#64748b',
                      }}
                    />
                  </div>
                  <span className="status-bar-count">{item.count}</span>
                </div>
              ))}
            </div>
          </section>

          {timeline.length > 0 && (
            <section className="stats-section">
              <h2>Timeline</h2>
              <div className="timeline-chart">
                <div className="timeline-bars">
                  {timeline.map((point) => (
                    <div key={point.month} className="timeline-column">
                      <div className="timeline-bar-wrapper">
                        <div
                          className="timeline-bar"
                          style={{ height: (point.count / maxTimelineCount) * 100 + '%' }}
                          title={point.month + ': ' + point.count + ' visit(s)'}
                        />
                      </div>
                      <span className="timeline-label">{point.month}</span>
                    </div>
                  ))}
                </div>
                <div className="timeline-cumulative">
                  <span className="timeline-cumulative-label">Cumulative</span>
                  <div className="timeline-cumulative-track">
                    <svg viewBox={'0 0 ' + timeline.length * 40 + ' 100'} preserveAspectRatio="none">
                      <polyline
                        fill="none"
                        stroke="#2563eb"
                        strokeWidth="2"
                        points={timeline
                          .map((point, index) => index * 40 + 20 + ',' + (100 - (point.cumulative / maxCumulative) * 90))
                          .join(' ')}
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </section>
          )}
        </>
      ) : null}
    </aside>
  );
}
