import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function Map({ mensas }) {
  // Center of Jena
  const center = [50.9282, 11.5870];
  const zoom = 14;

  return (
    <div className="h-[500px] w-full rounded-2xl overflow-hidden shadow-xl">
      <MapContainer 
        center={center} 
        zoom={zoom} 
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {mensas.map((mensa, index) => (
          <Marker 
            key={index} 
            position={[mensa.info.lat, mensa.info.lng]}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-bold text-lg mb-2">{mensa.info.name}</h3>
                <p className="text-sm text-gray-600 mb-2">{mensa.info.address}</p>
                <p className="text-sm font-semibold text-red-600">
                  {mensa.info.type === 'mensa' ? '🍽️ Dining Hall' : '☕ Cafeteria'}
                </p>
                {mensa.menu && mensa.menu.length > 0 && (
                  <p className="text-xs text-gray-500 mt-2">
                    {mensa.menu.length} dishes available today
                  </p>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default Map;