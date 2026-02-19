document.addEventListener("DOMContentLoaded", function () {
  const fromStop = document.getElementById("id_from_stop");
  const toStop = document.getElementById("id_to_stop");
  const seatsInput = document.getElementById("id_seats_booked");
  const availabilityBox = document.getElementById("available-seats");
  // Get the fare display element from your HTML
  const fareDisplay = document.getElementById("fare"); 

  const container = document.querySelector("[data-bus-id]");
  const busId = container ? container.dataset.busId : null;

  // Save ALL original to-stop options using their physical order (index) and save their fare
  const allToOptions = Array.from(toStop.options).map((opt, index) => ({
    value: opt.value,
    text: opt.text,
    originalIndex: index,
    fare: parseFloat(opt.dataset.fare) || 0 // Grab the fare we added in forms.py
  }));

  function filterToStops() {
    const selectedIndex = fromStop.selectedIndex;

    // Clear and rebuild the "To stop" dropdown
    toStop.innerHTML = "";
    
    allToOptions.forEach(function (optData) {
      // Keep the blank option, OR keep stops that are physically AFTER the selected From stop
      if (!optData.value || optData.originalIndex > selectedIndex) {
        const newOpt = document.createElement("option");
        newOpt.value = optData.value;
        newOpt.text = optData.text;
        // Keep the fare data attached to the new option
        if (optData.fare) newOpt.dataset.fare = optData.fare; 
        toStop.appendChild(newOpt);
      }
    });

    toStop.value = ""; 
    updateSeats();
    calculateFare(); // Calculate fare when stops change
  }

  function calculateFare() {
    // If we don't have both stops and a number of seats, set fare to 0
    if (!fromStop.value || !toStop.value || !seatsInput.value) {
      if (fareDisplay) fareDisplay.innerText = "₹0";
      return;
    }

    const startIdx = fromStop.selectedIndex;
    // Find the original index of the selected destination stop
    const destValue = toStop.value;
    const destOptData = allToOptions.find(opt => opt.value === destValue);
    const endIdx = destOptData ? destOptData.originalIndex : -1;
    
    if (endIdx <= startIdx) {
       if (fareDisplay) fareDisplay.innerText = "₹0";
       return;
    }

    let totalFareForOneSeat = 0;
    
    // Add up the fare for every stop *after* the starting stop, up to and including the destination stop
    for (let i = startIdx + 1; i <= endIdx; i++) {
        totalFareForOneSeat += allToOptions[i].fare;
    }

    const numberOfSeats = parseInt(seatsInput.value) || 1;
    const finalTotal = totalFareForOneSeat * numberOfSeats;

    // Update the HTML display
    if (fareDisplay) fareDisplay.innerText = `₹${finalTotal.toFixed(2)}`;
  }

  function updateSeats() {
    calculateFare(); // Recalculate fare whenever seats change
    
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
