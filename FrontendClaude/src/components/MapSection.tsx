import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin, TrendingUp, Building2, Landmark } from 'lucide-react';
import { Lead } from '../types';

interface MapSectionProps {
  stats: any;
  darkMode: boolean;
  onSelectCustomer?: (lead: Lead) => void;
}

// Fallback branch coordinates in case the backend doesn't output lat/long
const BRANCH_COORD_MAP: Record<string, [number, number]> = {
  'bangalore': [12.9716, 77.5946],
  'mumbai': [19.0760, 72.8777],
  'delhi': [28.7041, 77.1025],
  'chennai': [13.0827, 80.2707],
  'hyderabad': [17.3850, 78.4867],
};

export const MapSection: React.FC<MapSectionProps> = ({ stats, darkMode }) => {
  const [selectedBranch, setSelectedBranch] = useState<any>(null);

  // Extract branch list from Django team conversions dynamically
  const branches = stats?.teamStats?.conversions_per_branch || [];

  // Helper to create glowing SVG Leaflet markers matching Manipal branding (Blue and Gold/Amber)
  const createMarkerIcon = (isSelected: boolean) => {
    const color = isSelected ? '#e5b83b' : '#0076eb'; // gold if selected, blue otherwise
    const size = isSelected ? '28px' : '22px';
    const border = isSelected ? '4px solid white' : '3px solid white';
    return L.divIcon({
      html: `
        <div style="position: relative; width: ${size}; height: ${size}; cursor: pointer;">
          <div style="position: absolute; top: 0; left: 0; width: ${size}; height: ${size}; background: ${color}; border-radius: 50%; border: ${border}; box-shadow: 0 4px 10px rgba(0,0,0,0.3); z-index: 2;"></div>
          <div style="position: absolute; top: 0; left: 0; width: ${size}; height: ${size}; background: ${color}; border-radius: 50%; animation: ping 1.5s infinite; opacity: 0.4; z-index: 1;"></div>
        </div>
        <style>
          @keyframes ping {
            0% { transform: scale(1); opacity: 0.5; }
            100% { transform: scale(1.8); opacity: 0; }
          }
        </style>
      `,
      className: '',
      iconSize: isSelected ? [28, 28] : [22, 22],
      iconAnchor: isSelected ? [14, 14] : [11, 11]
    });
  };

  const getCoordinates = (branch: any, idx: number): [number, number] => {
    if (branch.latitude && branch.longitude) {
      const lat = parseFloat(branch.latitude);
      const lng = parseFloat(branch.longitude);
      if (!isNaN(lat) && !isNaN(lng)) {
        return [lat, lng];
      }
    }
    const branchName = branch.branch_name || '';
    const key = branchName.toLowerCase();
    for (const [city, coords] of Object.entries(BRANCH_COORD_MAP)) {
      if (key.includes(city)) return coords;
    }
    // Fallback coordinates in India
    return [20.5937 + (idx * 0.5), 78.9629 - (idx * 0.5)];
  };

  return (
    <div className={`rounded-2xl border overflow-hidden ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
      {/* Header */}
      <div className={`flex items-center justify-between px-5 py-4 border-b ${darkMode ? 'border-gray-700' : 'border-gray-100'}`}>
        <div>
          <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Geographic Footprint & Conversions</h3>
          <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Interactive branch network map</p>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>Live Branch Map</span>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row">
        {/* Leaflet Map Column */}
        <div className="flex-1 h-96 relative z-10">
          <MapContainer
            center={[20.5937, 78.9629]}
            zoom={4.5}
            style={{ width: '100%', height: '100%', background: darkMode ? '#1e293b' : '#f1f5f9' }}
            scrollWheelZoom={false}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              url={darkMode 
                ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                : "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
              }
            />
            {branches.map((branch: any, idx: number) => {
              const coords = getCoordinates(branch, idx);
              const isSelected = selectedBranch?.branch_id === branch.branch_id;

              return (
                <Marker
                  key={branch.branch_id}
                  position={coords}
                  icon={createMarkerIcon(isSelected)}
                  eventHandlers={{
                    click: () => {
                      setSelectedBranch(branch);
                    },
                  }}
                >
                  <Popup>
                    <div className="p-1 font-sans text-xs">
                      <strong className="text-gray-900 font-bold block mb-1">{branch.branch_name}</strong>
                      <div className="text-gray-600 space-y-0.5">
                        <p>Code: {branch.branch_code}</p>
                        <p>Applications: {branch.total_applications}</p>
                        <p>Disbursed: {branch.disbursed}</p>
                        <p className="text-indigo-600 font-semibold">Conversions: {(branch.conversion_rate_pct ?? branch.conversion_rate ?? 0).toFixed(1)}%</p>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}
          </MapContainer>
        </div>

        {/* Info sidebar */}
        <div className={`w-full lg:w-72 p-5 flex flex-col justify-between border-t lg:border-t-0 lg:border-l ${
          darkMode ? 'border-gray-700 bg-gray-900/20' : 'border-gray-100 bg-gray-50/50'
        }`}>
          <div>
            <h4 className={`text-xs font-bold uppercase tracking-wider mb-4 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              Branch Operations
            </h4>

            {selectedBranch ? (
              <div className="space-y-4 animate-fade-in">
                <div>
                  <h3 className={`text-base font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {selectedBranch.branch_name}
                  </h3>
                  <p className="text-xs text-indigo-500 font-medium">Code: {selectedBranch.branch_code}</p>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className={`p-3 rounded-xl border ${darkMode ? 'bg-gray-800/40 border-gray-700' : 'bg-white border-gray-200'}`}>
                    <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Applications</p>
                    <p className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                      {selectedBranch.total_applications}
                    </p>
                  </div>
                  <div className={`p-3 rounded-xl border ${darkMode ? 'bg-gray-800/40 border-gray-700' : 'bg-white border-gray-200'}`}>
                    <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Disbursed</p>
                    <p className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                      {selectedBranch.disbursed}
                    </p>
                  </div>
                </div>

                <div className={`p-4 rounded-xl border flex items-center gap-3 ${
                  darkMode ? 'bg-indigo-900/10 border-indigo-500/20' : 'bg-indigo-50 border-indigo-100'
                }`}>
                  <TrendingUp className="text-indigo-500" size={20} />
                  <div>
                    <p className={`text-xs ${darkMode ? 'text-indigo-300' : 'text-indigo-700'}`}>Conversion Rate</p>
                    <p className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-indigo-900'}`}>
                      {(selectedBranch.conversion_rate_pct ?? selectedBranch.conversion_rate ?? 0).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center">
                <MapPin className={`mx-auto mb-2 ${darkMode ? 'text-gray-600' : 'text-gray-300'}`} size={32} />
                <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                  Select a branch marker on the map to view detailed regional loan conversions.
                </p>
              </div>
            )}
          </div>

          <div className={`mt-6 pt-4 border-t text-xxs leading-relaxed ${darkMode ? 'border-gray-800 text-gray-500' : 'border-gray-200 text-gray-400'}`}>
            <div className="flex items-center gap-1 mb-1">
              <Landmark size={10} />
              <span>National Operations Hub</span>
            </div>
            Map integrates with real coordinate metrics for active branch networks mapped from your backend system.
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapSection;
