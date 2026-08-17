export default function MapLegend() {
  return (
    <aside className="map-legend">
      <span>
        <i className="legend-swatch unlit" />
        Not visited
      </span>
      <span>
        <i className="legend-swatch lit" />
        Visited
      </span>
    </aside>
  );
}
