import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in React-Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

L.Marker.prototype.options.icon = DefaultIcon;

// Component to handle map bounds updates
const MapBoundsController: React.FC<{
  targetTrack: TrackPoint[];
  detectors: Coordinate[];
  jointMovementTracks: Array<{ matches: Array<{ latitude: number; longitude: number }> }>;
  routes: Route[];
}> = ({ targetTrack, detectors, jointMovementTracks, routes }) => {
  const map = useMap();

  useEffect(() => {
    const bounds = L.latLngBounds([]);
    let hasBounds = false;

    [...targetTrack, ...detectors].forEach(point => {
      if (point.latitude && point.longitude) {
        bounds.extend([point.latitude, point.longitude]);
        hasBounds = true;
      }
    });

    jointMovementTracks.forEach(track => {
      track.matches.forEach(match => {
        if (match.latitude && match.longitude) {
          bounds.extend([match.latitude, match.longitude]);
          hasBounds = true;
        }
      });
    });

    routes.forEach(route => {
      route.coordinates.forEach(coord => {
        if (coord.latitude && coord.longitude) {
          bounds.extend([coord.latitude, coord.longitude]);
          hasBounds = true;
        }
      });
    });

    if (hasBounds && bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [map, targetTrack, detectors, jointMovementTracks, routes]);

  return null;
};

interface Coordinate {
  latitude: number;
  longitude: number;
  detector_id?: string;
}

interface TrackPoint extends Coordinate {
  timestamp?: string;
  speed?: number;
}

interface Route {
  coordinates: Coordinate[];
  route_signature?: string;
  total_vehicles?: number;
  intensity_per_hour?: number;
}

interface TrafficMapProps {
  center?: [number, number];
  zoom?: number;
  detectors?: Coordinate[];
  targetTrack?: TrackPoint[];
  jointMovementTracks?: Array<{
    vehicle_id: string;
    matches: Array<{
      latitude: number;
      longitude: number;
      detector_id: string;
    }>;
  }>;
  routes?: Route[];
  selectedRoute?: Route | null;
  height?: string;
}

const TrafficMap: React.FC<TrafficMapProps> = ({
  center = [54.7826, 32.0453], // Смоленск по умолчанию
  zoom = 13,
  detectors = [],
  targetTrack = [],
  jointMovementTracks = [],
  routes = [],
  selectedRoute = null,
  height = '600px',
}) => {
  // Colors for visualization
  const routeColors = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF',
    '#00FFFF', '#FFA500', '#800080', '#FFC0CB', '#A52A2A'
  ];

  return (
    <div style={{ height, width: '100%' }} className="rounded-lg overflow-hidden border border-gray-300">
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
      >
        <MapBoundsController
          targetTrack={targetTrack}
          detectors={detectors}
          jointMovementTracks={jointMovementTracks}
          routes={routes}
        />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Detectors */}
        {detectors.map((detector, idx) => (
          <Marker
            key={`detector-${idx}`}
            position={[detector.latitude, detector.longitude]}
          >
            <Popup>
              <div>
                <strong>Детектор:</strong> {detector.detector_id || `#${idx + 1}`}
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Target Vehicle Track */}
        {targetTrack.length > 0 && (
          <Polyline
            positions={targetTrack.map(point => [point.latitude, point.longitude])}
            color="#FF0000"
            weight={4}
            opacity={0.8}
          />
        )}

        {/* Joint Movement Matches */}
        {jointMovementTracks.map((track, trackIdx) => (
          <React.Fragment key={`joint-${trackIdx}`}>
            <Polyline
              positions={track.matches.map(match => [match.latitude, match.longitude])}
              color="#00FF00"
              weight={3}
              opacity={0.6}
              dashArray="5, 5"
            />
            {track.matches.map((match, matchIdx) => (
              <CircleMarker
                key={`match-${trackIdx}-${matchIdx}`}
                center={[match.latitude, match.longitude]}
                radius={6}
                fillColor="#00FF00"
                color="#000000"
                weight={1}
                opacity={0.8}
                fillOpacity={0.6}
              >
                <Popup>
                  <div>
                    <strong>Совместное движение</strong><br />
                    ТС: {track.vehicle_id}<br />
                    Детектор: {match.detector_id}
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </React.Fragment>
        ))}

        {/* Routes (Top-N loaded routes) */}
        {routes.map((route, idx) => {
          const isSelected = selectedRoute?.route_signature === route.route_signature;
          const color = routeColors[idx % routeColors.length];
          
          return (
            <Polyline
              key={`route-${idx}`}
              positions={route.coordinates.map(coord => [coord.latitude, coord.longitude])}
              color={color}
              weight={isSelected ? 6 : (route.intensity_per_hour ? Math.max(2, route.intensity_per_hour / 5) : 2)}
              opacity={isSelected ? 1.0 : 0.7}
            />
          );
        })}

        {/* Route markers */}
        {routes.map((route, idx) => {
          const color = routeColors[idx % routeColors.length];
          return route.coordinates.map((coord, coordIdx) => (
            <CircleMarker
              key={`route-marker-${idx}-${coordIdx}`}
              center={[coord.latitude, coord.longitude]}
              radius={4}
              fillColor={color}
              color="#000000"
              weight={1}
              opacity={0.8}
              fillOpacity={0.6}
            >
              <Popup>
                <div>
                  <strong>Маршрут #{idx + 1}</strong><br />
                  ТС: {route.total_vehicles || 'N/A'}<br />
                  Интенсивность: {route.intensity_per_hour?.toFixed(2) || 'N/A'} ТС/час
                </div>
              </Popup>
              </CircleMarker>
            ));
        })}
      </MapContainer>
    </div>
  );
};

export default TrafficMap;
