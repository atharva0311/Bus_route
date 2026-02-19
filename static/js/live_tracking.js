// document.addEventListener("DOMContentLoaded", function () {
//     const map = L.map('map').setView([20.5937, 78.9629], 5);
//     L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);

//     const busMarkers = {};

//     const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
//     const socket = new WebSocket(`${ws_scheme}://${window.location.host}/ws/live-buses/`);

//     socket.onmessage = function (event) {
//         const data = JSON.parse(event.data);
//         const busId = data.bus_id;
//         const latlng = [data.latitude, data.longitude];

//         const popupContent = `
//             <b>${data.bus_name || 'Bus '+busId}</b><br>
//             Speed: ${data.speed} km/h<br>
//             Status: ${data.status || 'running'}
//         `;

//         if (busMarkers[busId]) {
//             busMarkers[busId].setLatLng(latlng);
//             busMarkers[busId].setPopupContent(popupContent);
//         } else {
//             busMarkers[busId] = L.marker(latlng).addTo(map).bindPopup(popupContent);
//         }
//     };

//     socket.onopen = () => console.log("Connected to live bus WebSocket");
//     socket.onclose = () => console.log("Disconnected from live bus WebSocket");

//     // Fetch initial bus positions from API
//     async function fetchActiveBuses() {
//         try {
//             const res = await fetch('/tracking/api/active-buses/');
//             const data = await res.json();
//             data.buses.forEach(bus => {
//                 socket.send(JSON.stringify({
//                     bus_id: bus.bus_id,
//                     latitude: bus.latitude,
//                     longitude: bus.longitude,
//                     speed: bus.speed,
//                     status: bus.status,
//                     bus_name: bus.bus_name
//                 }));
//             });
//         } catch (err) {
//             console.error("Error fetching active buses:", err);
//         }
//     }

//     fetchActiveBuses();
//     setInterval(fetchActiveBuses, 5000); // refresh every 5 sec
// });


document.addEventListener("DOMContentLoaded", function () {
    const map = L.map('map').setView([20.5937, 78.9629], 5); // center India
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    const busMarkers = {};

    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${ws_scheme}://${window.location.host}/ws/live-buses/`);

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        const busId = data.bus_id;
        const latlng = [data.latitude, data.longitude];

        const popupContent = `
            <b>${data.bus_name} (${data.bus_number})</b><br>
            Route: ${data.route}<br>
            Speed: ${data.speed} km/h<br>
            Status: ${data.status}<br>
            Next Stop: ${data.next_stop}<br>
            ETA: ${data.eta ? new Date(data.eta).toLocaleTimeString() : 'N/A'}
        `;

        if (busMarkers[busId]) {
            busMarkers[busId].setLatLng(latlng);
            busMarkers[busId].setPopupContent(popupContent);
        } else {
            busMarkers[busId] = L.marker(latlng)
                .addTo(map)
                .bindPopup(popupContent);
        }
    };

    socket.onopen = () => console.log("Connected to live bus WebSocket");
    socket.onclose = () => console.log("Disconnected from live bus WebSocket");
});
