document.addEventListener("DOMContentLoaded", function () {
  const fromStop = document.getElementById("id_from_stop");
  const toStop = document.getElementById("id_to_stop");
  const seatsInput = document.getElementById("id_seats_booked");
  const availabilityBox = document.getElementById("available-seats");

  const container = document.querySelector("[data-bus-id]");
  const busId = container ? container.dataset.busId : null;

  // Save ALL original to-stop options when page loads
  const allToOptions = Array.from(toStop.options).map(opt => ({
    value: opt.value,
    text: opt.text,
    sequence: parseInt(opt.dataset.sequence) || 0
  }));

  function filterToStops() {
    const selectedOption = fromStop.options[fromStop.selectedIndex];
    const fromSeq = selectedOption ? parseInt(selectedOption.dataset.sequence) || 0 : 0;

    // Clear and rebuild the "To stop" dropdown
    toStop.innerHTML = "";
    allToOptions.forEach(function (optData) {
      if (!optData.value || optData.sequence > fromSeq) {
        const newOpt = document.createElement("option");
        newOpt.value = optData.value;
        newOpt.text = optData.text;
        if (optData.sequence) newOpt.dataset.sequence = optData.sequence;
        toStop.appendChild(newOpt);
      }
    });

    toStop.value = "";
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