import React from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import type { BranchGeoNode } from "../api/customers";
import { formatInr } from "./ui";

import "leaflet/dist/leaflet.css";

// Fix Leaflet marker icon asset paths for bundlers
const customMarkerIcon = new L.Icon({
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

interface CustomerMapProps {
  nodes: BranchGeoNode[];
  onNodeClick: (node: BranchGeoNode) => void;
}

// Controller component to programmatically handle Fit to India or center changes
const MapController: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  React.useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
};

export const CustomerMap: React.FC<CustomerMapProps> = ({
  nodes,
  onNodeClick,
}) => {
  const defaultCenter: [number, number] = [20.5937, 78.9629]; // India center
  const defaultZoom = 5;

  const [mapState, setMapState] = React.useState({
    center: defaultCenter,
    zoom: defaultZoom,
  });

  const resetMap = () => {
    setMapState({
      center: defaultCenter,
      zoom: defaultZoom,
    });
  };

  const fitToIndia = () => {
    setMapState({
      center: [22.9734, 78.6569],
      zoom: 5,
    });
  };

  return (
    <div className="map-view-card">
      <div className="map-controls">
        <button className="btn-map-action" onClick={fitToIndia}>
          🇮🇳 Fit to India
        </button>
        <button className="btn-map-action" onClick={resetMap}>
          🔄 Reset Map
        </button>
      </div>

      <div style={{ height: "480px", borderRadius: "var(--radius-md)", overflow: "hidden", position: "relative" }}>
        <MapContainer
          center={mapState.center}
          zoom={mapState.zoom}
          style={{ height: "100%", width: "100%" }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />
          <MapController center={mapState.center} zoom={mapState.zoom} />

          {nodes.map((node) => {
            return (
              <Marker
                key={node.branchId}
                position={[node.latitude, node.longitude]}
                icon={customMarkerIcon}
                eventHandlers={{
                  click: () => onNodeClick(node),
                }}
              >
                <Popup>
                  <div className="map-popup-content">
                    <h4 style={{ color: "var(--accent-blue)", marginBottom: "4px" }}>
                      {node.branchName}
                    </h4>
                    <p style={{ margin: "2px 0", fontSize: "11px", color: "#64748b" }}>
                      Code: {node.branchCode}
                    </p>
                    <p style={{ margin: "2px 0", fontSize: "12px" }}>
                      Applications: <strong>{node.applications}</strong>
                    </p>
                    <p style={{ margin: "2px 0", fontSize: "12px" }}>
                      Disbursed: <strong>{formatInr(node.disbursed)}</strong>
                    </p>
                    <p style={{ margin: "2px 0", fontSize: "12px", color: "var(--accent-emerald)" }}>
                      Conversion: <strong>{node.conversionRate}%</strong>
                    </p>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
};
