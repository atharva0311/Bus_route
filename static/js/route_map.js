let map = L.map("map").setView([19.0760, 72.8777], 6);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18
}).addTo(map);

let markers = [];
let polyline = L.polyline([], { color: "blue" }).addTo(map);
let stops = [];

map.on("click", function (e) {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;

    const marker = L.marker([lat, lng]).addTo(map);
    markers.push(marker);

    polyline.addLatLng([lat, lng]);

    const stopIndex = stops.length + 1;

    stops.push({
        name: "Stop " + stopIndex,
        lat: lat,
        lng: lng
    });

    document.getElementById("stops_json").value = JSON.stringify(stops);

    // Source
    if (stops.length === 1) {
        document.querySelector("[name=source_name]").value = "Source";
        document.querySelector("[name=source_lat]").value = lat;
        document.querySelector("[name=source_lng]").value = lng;
    }

    // Destination (always last)
    if (stops.length >= 2) {
        document.querySelector("[name=destination_name]").value = "Destination";
        document.querySelector("[name=destination_lat]").value = lat;
        document.querySelector("[name=destination_lng]").value = lng;
    }
});
