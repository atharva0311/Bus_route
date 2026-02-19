document.addEventListener("DOMContentLoaded", function () {
  const fromStop = document.getElementById("id_from_stop");
  const toStop = document.getElementById("id_to_stop");
  const seatsInput = document.getElementById("id_seats_booked");
  const fareBox = document.getElementById("fare");
  const availabilityBox = document.getElementById("available-seats");
  const busId = document.body.dataset.busId;

  function filterToStops() {
    const fromSeq = fromStop.options[fromStop.selectedIndex]?.dataset.sequence;
    for (let option of toStop.options) {
      const toSeq = option.dataset.sequence;
      option.style.display = toSeq > fromSeq ? "block" : "none";
    }
    toStop.value = "";
    updateFareAndSeats();
  }

  function updateFareAndSeats() {
    if (!fromStop.value || !toStop.value || !seatsInput.value) return;

    fetch(`/fare-preview/?from=${fromStop.value}&to=${toStop.value}&seats=${seatsInput.value}`)
      .then(res => res.json())
      .then(data => {
        fareBox.innerText = data.error ? "₹0" : `₹${data.fare} (${data.distance} km)`;
      })
      .catch(() => { fareBox.innerText = "₹0"; });

    fetch(`/buses/api/seats/${busId}/`)
      .then(res => res.json())
      .then(data => {
        if (availabilityBox) availabilityBox.innerText = `${data.available_seats} / ${data.total_seats} seats available`;
        if (parseInt(seatsInput.value) > data.available_seats) seatsInput.setCustomValidity("Not enough seats available for this route.");
        else seatsInput.setCustomValidity("");
      })
      .catch(() => { if (availabilityBox) availabilityBox.innerText = ""; });
  }

  fromStop.addEventListener("change", filterToStops);
  toStop.addEventListener("change", updateFareAndSeats);
  seatsInput.addEventListener("input", updateFareAndSeats);
});
