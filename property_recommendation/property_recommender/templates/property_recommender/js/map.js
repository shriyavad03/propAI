document.addEventListener('DOMContentLoaded', (event) => {
    var map = L.map('map').setView([12.9716, 77.5946], 12); // Centered on Bangalore

    // Add Mapbox tiles
    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1Ijoic2hyaXlhdmFkIiwiYSI6ImNseGtqMWZkOTAyZmQycnIxNmo4am1vc2oifQ.Bzg0Vp9U0ilTM5a8sv8yTw', {
        maxZoom: 18,
        id: 'mapbox/streets-v11',
        tileSize: 512,
        zoomOffset: -1,
        accessToken: 'pk.eyJ1Ijoic2hyaXlhdmFkIiwiYSI6ImNseGtqMWZkOTAyZmQycnIxNmo4am1vc2oifQ.Bzg0Vp9U0ilTM5a8sv8yTw'
    }).addTo(map);

    fetch('/frequent_locations/')
        .then(response => response.json())
        .then(data => {
            var heat = L.heatLayer(data.map(loc => [loc.lat, loc.lng, loc.count]), {
                radius: 20
            }).addTo(map);
        })
        .catch(error => console.error('Error fetching location data:', error));
});

document.addEventListener('DOMContentLoaded', function() {
    fetchLocationData();
    fetchTrafficData();
    fetchRoomsData();
});

function fetchLocationData() {
    fetch('/api/location_data/')  // Replace with your endpoint for location data
        .then(response => response.json())
        .then(data => {
            // Initialize Mapbox GL map
            mapboxgl.accessToken = 'pk.eyJ1Ijoic2hyaXlhdmFkIiwiYSI6ImNseGtqMWZkOTAyZmQycnIxNmo4am1vc2oifQ.Bzg0Vp9U0ilTM5a8sv8yTw';
            var map = new mapboxgl.Map({
                container: 'map',
                style: 'mapbox://styles/mapbox/streets-v11',
                center: [12.9716, 77.5946], // Example center coordinates
                zoom: 12
            });

            // Prepare marker data based on location frequency
            var markerData = data.locations.map(location => ({
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [location.longitude, location.latitude]
                },
                properties: {
                    title: location.name,
                    description: 'Frequency: ' + location.frequency
                }
            }));

            // Add markers to the map
            markerData.forEach(marker => {
                // create a HTML element for each feature
                var el = document.createElement('div');
                el.className = 'marker';

                // make a marker for each feature and add to the map
                new mapboxgl.Marker(el)
                    .setLngLat(marker.geometry.coordinates)
                    .setPopup(new mapboxgl.Popup({ offset: 25 }) // add popups
                    .setHTML('<h3>' + marker.properties.title + '</h3><p>' + marker.properties.description + '</p>'))
                    .addTo(map);
            });
        })
        .catch(error => console.error('Error fetching location data:', error));
}
