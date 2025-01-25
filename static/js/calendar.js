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
                dayDiv.addEventListener("click", function (event) {
                    showDetectionDetails(event, formattedDate, detections);
                });
            }

            calendarGrid.appendChild(dayDiv);
        }

        monthDiv.appendChild(calendarGrid);
        calendarContainer.appendChild(monthDiv);
    }
}

function showDetectionDetails(event, date, detections) {
    const existingPopup = document.querySelector(".detection-popup");
    if (existingPopup) {
        existingPopup.remove();
    }

    const popup = document.createElement("div");
    popup.className = "detection-popup";

    const popupContent = document.createElement("div");
    popupContent.className = "detection-popup-content";

    const closeButton = document.createElement("span");
    closeButton.className = "close-popup";
    closeButton.textContent = "×";
    closeButton.onclick = () => popup.remove();
    popupContent.appendChild(closeButton);

    const title = document.createElement("h3");
    title.textContent = `Detections for ${date}`;
    popupContent.appendChild(title);

    const detectionList = document.createElement("ul");
    detectionList.className = "detection-list";

    detections.forEach(time => {
        if (time) {
            const listItem = document.createElement("li");
            listItem.className = "detection-list-item";

            const timeLink = document.createElement("a");
            timeLink.href = `/dashboard?timestamp=${date} ${time}`;
            timeLink.textContent = `Time: ${time}`;
            timeLink.className = "detection-time-link";
            listItem.appendChild(timeLink);

            detectionList.appendChild(listItem);
        }
    });

    popupContent.appendChild(detectionList);
    popup.appendChild(popupContent);
    document.body.appendChild(popup);

    const rect = event.target.getBoundingClientRect();
    popup.style.top = `${rect.top + window.scrollY + rect.height}px`;
    popup.style.left = `${rect.left + window.scrollX}px`;
}
