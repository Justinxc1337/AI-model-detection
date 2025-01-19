document.addEventListener("DOMContentLoaded", function () {
    const detectionDatesDiv = document.getElementById("detection-data");
    if (detectionDatesDiv) {
        const detectionDates = JSON.parse(detectionDatesDiv.textContent);
        console.log("Detection Dates from Backend:", detectionDates);

        // Generate the calendar and highlight dates
        generateCalendar(detectionDates);
    } else {
        console.error("Detection data div not found.");
    }
});

function generateCalendar(detectionDates) {
    const calendarContainer = document.getElementById("calendar");
    if (!calendarContainer) {
        console.error("Calendar container not found.");
        return;
    }

    const currentYear = 2025;

    // Process detection dates to group detections by day
    const formattedDetectionDates = detectionDates.reduce((acc, dateTime) => {
        const [day, month, year, time] = dateTime.split(" ");
        const date = `${day} ${month} ${year}`;
        if (!acc[date]) {
            acc[date] = [];
        }
        acc[date].push(time);
        return acc;
    }, {});

    for (let month = 0; month < 12; month++) {
        const monthDiv = document.createElement("div");
        monthDiv.className = "month-container";

        const monthHeader = document.createElement("div");
        monthHeader.className = "month-header";
        monthHeader.textContent = new Date(currentYear, month).toLocaleString("en-US", { month: "long" }) + " " + currentYear;
        monthDiv.appendChild(monthHeader);

        const calendarGrid = document.createElement("div");
        calendarGrid.className = "calendar-grid";

        const daysOfWeek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
        daysOfWeek.forEach(day => {
            const dayDiv = document.createElement("div");
            dayDiv.className = "calendar-day";
            dayDiv.textContent = day;
            calendarGrid.appendChild(dayDiv);
        });

        const firstDayOfMonth = new Date(currentYear, month, 1);
        const daysInMonth = new Date(currentYear, month + 1, 0).getDate();

        let firstDayIndex = firstDayOfMonth.getDay() - 1;
        if (firstDayIndex === -1) firstDayIndex = 6;

        for (let i = 0; i < firstDayIndex; i++) {
            const emptyCell = document.createElement("div");
            calendarGrid.appendChild(emptyCell);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const dayDiv = document.createElement("div");
            dayDiv.className = "calendar-day";

            const formattedDate = `${String(day).padStart(2, "0")} ${String(month + 1).padStart(2, "0")} ${currentYear}`;
            const detections = formattedDetectionDates[formattedDate];

            const dateText = document.createElement("div");
            dateText.className = "date-text";
            dateText.textContent = day;
            dayDiv.appendChild(dateText);

            if (detections) {
                dayDiv.classList.add("detection-day");

                // Display detection count below the date
                const countBadge = document.createElement("div");
                countBadge.className = "detection-count";
                countBadge.textContent = `DTs: ${detections.length}`;
                dayDiv.appendChild(countBadge);

                // Add click event to show detection details
                dayDiv.addEventListener("click", function () {
                    showDetectionDetails(formattedDate, detections);
                });
            }

            calendarGrid.appendChild(dayDiv);
        }

        monthDiv.appendChild(calendarGrid);
        calendarContainer.appendChild(monthDiv);
    }
}

function showDetectionDetails(date, detections) {
    const detailsContainer = document.getElementById("detection-details");
    detailsContainer.innerHTML = `<h3>Detections for ${date}</h3>`;
    detections.forEach(time => {
        const timeDiv = document.createElement("div");
        timeDiv.className = "detection-time";
        timeDiv.textContent = `Time: ${time}`;
        detailsContainer.appendChild(timeDiv);
    });
}