document.addEventListener("DOMContentLoaded", function () {
  const fromStop = document.getElementById("id_from_stop");
  const toStop = document.getElementById("id_to_stop");
  const seatsInput = document.getElementById("id_seats_booked");
  const availabilityBox = document.getElementById("available-seats");
  const fareDisplay = document.getElementById("fare"); 

  const container = document.querySelector("[data-bus-id]");
  const busId = container ? container.dataset.busId : null;

  // Save ALL original to-stop options using their physical order (index)
  const allToOptions = Array.from(toStop.options).map((opt, index) => ({
    value: opt.value,
    text: opt.text,
    originalIndex: index,
    // 🚀 Grab the price from our bulletproof window object!
    fare: window.STOP_FARES[opt.value] || 0 
  }));

  function filterToStops() {
    const selectedIndex = fromStop.selectedIndex;
    toStop.innerHTML = "";
    
    allToOptions.forEach(function (optData) {
      if (!optData.value || optData.originalIndex > selectedIndex) {
        const newOpt = document.createElement("option");
        newOpt.value = optData.value;
        newOpt.text = optData.text;
        toStop.appendChild(newOpt);
      }
    });

    toStop.value = ""; 
    updateSeats();
    calculateFare(); 
  }

  function calculateFare() {
    if (!fromStop.value || !toStop.value || !seatsInput.value) {
      if (fareDisplay) fareDisplay.innerText = "₹0.00";
      return;
    }

    const startIdx = fromStop.selectedIndex;
    const destValue = toStop.value;
    const destOptData = allToOptions.find(opt => opt.value === destValue);
    const endIdx = destOptData ? destOptData.originalIndex : -1;
    
    if (endIdx <= startIdx) {
       if (fareDisplay) fareDisplay.innerText = "₹0.00";
       return;
    }

    let totalFareForOneSeat = 0;
    
    for (let i = startIdx + 1; i <= endIdx; i++) {
        totalFareForOneSeat += allToOptions[i].fare;
    }

    const numberOfSeats = parseInt(seatsInput.value) || 1;
    const finalTotal = totalFareForOneSeat * numberOfSeats;

    if (fareDisplay) fareDisplay.innerText = `₹${finalTotal.toFixed(2)}`;
  }

  function updateSeats() {
    calculateFare(); 
    
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
