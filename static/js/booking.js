document.addEventListener("DOMContentLoaded", function () {
  const fromStop = document.getElementById("id_from_stop");
  const toStop = document.getElementById("id_to_stop");
  const seatsInput = document.getElementById("id_seats_booked");
  const availabilityBox = document.getElementById("available-seats");

  const container = document.querySelector("[data-bus-id]");
  const busId = container ? container.dataset.busId : null;

  // Save ALL original to-stop options using their physical order (index)
  const allToOptions = Array.from(toStop.options).map((opt, index) => ({
    value: opt.value,
    text: opt.text,
    originalIndex: index
  }));

  function filterToStops() {
    // Get the physical position of the selected "From" stop
    const selectedIndex = fromStop.selectedIndex;

    // Clear and rebuild the "To stop" dropdown
    toStop.innerHTML = "";
    
    allToOptions.forEach(function (optData) {
      // Keep the blank option, OR keep stops that are physically AFTER the selected From stop
      if (!optData.value || optData.originalIndex > selectedIndex) {
        const newOpt = document.createElement("option");
        newOpt.value = optData.value;
        newOpt.text = optData.text;
        toStop.appendChild(newOpt);
      }
    });

    toStop.value = ""; // Reset the destination selection
    updateSeats();
  }

  function updateSeats() {
    if (!fromStop.value || !toStop.value || !seatsInput.value) return;
    if (!busId) return;

    fetch(`/buses/api/seats/${busId}/`)
      .then(res => res.json())
      .then(data => {
        if (availabilityBox)
          availabilityBox.innerText = `${data.available_seats} / ${data.total_seats} seats available`;
        if (parseInt(seatsInput.value) > data.available_seats)
          seatsInput.setCustomValidity("Not enough seats available.");
        else
          seatsInput.setCustomValidity("");
      })
      .catch(() => {
        if (availabilityBox) availabilityBox.innerText = "Unable to load seats";
      });
  }

  fromStop.addEventListener("change", filterToStops);
  toStop.addEventListener("change", updateSeats);
  seatsInput.addEventListener("input", updateSeats);
});
