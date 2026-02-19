document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("seat-layout");
    if (!container) return;

    const busId = container.dataset.busId;
    const dateInput = document.getElementById("id_travel_date");
    const seatCountInput = document.getElementById("id_seats_booked");

    let selectedSeats = new Set();

    async function loadSeats() {
        const date = dateInput.value;
        if (!date) return;

        const res = await fetch(`/bookings/api/seats/${busId}/?date=${date}`);
        const data = await res.json();

        container.innerHTML = "";
        selectedSeats.clear();

        data.seats.forEach(seat => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "seat";

            btn.textContent = seat.number;

            if (seat.is_booked) {
                btn.classList.add("seat-booked");
                btn.disabled = true;
            }

            btn.onclick = () => toggleSeat(seat.number, btn);
            container.appendChild(btn);
        });
    }

    function toggleSeat(seatNumber, button) {
        if (selectedSeats.has(seatNumber)) {
            selectedSeats.delete(seatNumber);
            button.classList.remove("seat-selected");
        } else {
            selectedSeats.add(seatNumber);
            button.classList.add("seat-selected");
        }

        seatCountInput.value = selectedSeats.size;
        document.getElementById("selected-seats-input").value =
            Array.from(selectedSeats).join(",");
    }

    dateInput.addEventListener("change", loadSeats);
    loadSeats();
});
