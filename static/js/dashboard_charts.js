document.addEventListener("DOMContentLoaded", function () {

    if (typeof bookingData === "undefined") return;

    // ------------------------
    // Booking Status Chart
    // ------------------------
    const bookingLabels = bookingData.map(b => 
        b.status.charAt(0).toUpperCase() + b.status.slice(1)
    );
    const bookingCounts = bookingData.map(b => b.count);

    new Chart(document.getElementById("bookingChart"), {
        type: "doughnut",
        data: {
            labels: bookingLabels.length ? bookingLabels : ["No Data"],
            datasets: [{
                data: bookingCounts.length ? bookingCounts : [1],
                backgroundColor: [
                    "#28a745",
                    "#ffc107",
                    "#dc3545",
                    "#6c757d"
                ]
            }]
        },
        options: { responsive: true }
    });

    // ------------------------
    // Trip Status Chart
    // ------------------------
    const tripLabels = tripData.map(t =>
        t.status.replace("_", " ").toUpperCase()
    );
    const tripCounts = tripData.map(t => t.count);

    new Chart(document.getElementById("tripChart"), {
        type: "doughnut",
        data: {
            labels: tripLabels.length ? tripLabels : ["No Data"],
            datasets: [{
                data: tripCounts.length ? tripCounts : [1],
                backgroundColor: [
                    "#17a2b8",
                    "#28a745",
                    "#ffc107",
                    "#dc3545",
                    "#6c757d"
                ]
            }]
        },
        options: { responsive: true }
    });

    // ------------------------
    // Daily bookings chart
    // ------------------------
    const dailyLabels = dailyData.map(d => d.date);
    const dailyCounts = dailyData.map(d => d.count);

    new Chart(document.getElementById("dailyChart"), {
        type: "bar",
        data: {
            labels: dailyLabels,
            datasets: [{
                label: "Bookings",
                data: dailyCounts,
                backgroundColor: "#e63946"
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});
