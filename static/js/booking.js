document.addEventListener("DOMContentLoaded", function () {
  const fromStop = document.getElementById("id_from_stop");
  const toStop = document.getElementById("id_to_stop");
  const seatsInput = document.getElementById("id_seats_booked");
  const fareBox = document.getElementById("fare");
  const availabilityBox = document.getElementById("available-seats");

  // Fix: read bus-id from the container div, not body
  const container = document.querySelector("[data-bus-id]");
  const busId = container ? container.dataset.busId : null;

  function filterToStops() {
    const selectedOption = fromStop.options[fromStop.selectedIndex];
    const fromSeq = selectedOption ? parseInt(selectedOption.dataset.sequence) : 0;

    for (let option of toStop.options) {
      if (!option.value) {
        // Keep the empty "--------" option visible
        option.style.display = "block";
        continue;
      }
      const toSeq = parseInt(option.dataset.sequence);
      option.style.display = toSeq > fromSeq ? "block" : "none";
    }
    toStop.value = "";
    updateFareAndSeats();
  }

  function updateFareAndSeats() {
    if (!fromStop.value || !toStop.value || !seatsInput.value) return;

    // Update available seats
    if (busId) {
      fetch(`/buses/api/seats/${busId}/`)
        .then(res => res.json())
        .then(data => {
          if (availabilityBox) availabilityBox.innerText = `${data.available_seats} / ${data.total_seats} seats available`;
          if (parseInt(seatsInput.value) > data.available_seats) seatsInput.setCustomValidity("Not enough seats available for this route.");
          else seatsInput.setCustomValidity("");
        })
        .catch(() => { if (availabilityBox) availabilityBox.innerText = ""; });
    }
  }

  fromStop.addEventListener("change", filterToStops);
  toStop.addEventListener("change", updateFareAndSeats);
  seatsInput.addEventListener("input", updateFareAndSeats);
});
