document.addEventListener("DOMContentLoaded", function () {
    const detectionDatesDiv = document.getElementById("detection-data");
    if (detectionDatesDiv) {
        fetchDetectionFiles();
    } else {
        console.error("Detection data div not found.");
    }
});

async function fetchDetectionFiles() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/detection-files');
        const filenames = await response.json();
        console.log("Detection Files from Backend:", filenames);

        // Generate the calendar and highlight dates
        const detectionDates = filenames.map(filename => {
            const dateMatch = filename.match(/(\d{2})D, (\d{2})M, (\d{4})Y/);
            if (dateMatch) {
                const [_, day, month, year] = dateMatch;
                return `${String(day).padStart(2, "0")} ${String(month).padStart(2, "0")} ${year}`;
            }
        }).filter(Boolean);

        generateCalendar(detectionDates, filenames);
    } catch (error) {
        console.error('Error fetching detection files:', error);
    }
}

function generateCalendar(detectionDates, filenames) {
    const calendarContainer = document.getElementById("calendar");
    if (!calendarContainer) {
        console.error("Calendar container not found.");
        return;
    }

    const currentYear = 2025;

    // Group detections by day
    const formattedDetectionDates = detectionDates.reduce((acc, date, index) => {
        if (!acc[date]) {
            acc[date] = [];
        }
        const timestamp = filenames[index].match(/(\d{2})D, (\d{2})M, (\d{4})Y_(\d{2})H, (\d{2})M, (\d{2})S/);
        if (timestamp) {
            const [_, day, month, year, hour, minute, second] = timestamp;
            const formattedTimestamp = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')} ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:${String(second).padStart(2, '0')}`;
            acc[date].push(formattedTimestamp);
        }
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

                const countBadge = document.createElement("div");
                countBadge.className = "detection-count";
                countBadge.textContent = `DTs: ${detections.length}`;
                dayDiv.appendChild(countBadge);

                // On clicking the date, show the detection details above the date
                dayDiv.addEventListener("click", function () {
                    showDetectionDetails(dayDiv, formattedDate, detections);
                });
            }

            calendarGrid.appendChild(dayDiv);
        }

        monthDiv.appendChild(calendarGrid);
        calendarContainer.appendChild(monthDiv);
    }
}

let currentDetailsBox = null;

function showDetectionDetails(dayDiv, date, detections) {
    if (currentDetailsBox) {
        currentDetailsBox.remove();
    }

    // Create a new details box
    const detailsBox = document.createElement("div");
    detailsBox.className = "detection-details-box";

    const detailsTitle = document.createElement("h4");
    detailsTitle.textContent = `Detections on ${date}`;
    detailsBox.appendChild(detailsTitle);

    const detailsList = document.createElement("ul");
    detections.forEach(timestamp => {
        const timeMatch = timestamp.match(/\d{2}:\d{2}:\d{2}/);
        if (timeMatch) {
            const li = document.createElement("li");
            li.textContent = `Timestamp: ${timeMatch[0]}`;
            detailsList.appendChild(li);
        }
    });
    detailsBox.appendChild(detailsList);

    dayDiv.insertBefore(detailsBox, dayDiv.firstChild);

    currentDetailsBox = detailsBox;

    document.addEventListener('click', function (event) {
        if (!detailsBox.contains(event.target) && !dayDiv.contains(event.target)) {
            detailsBox.remove();
            currentDetailsBox = null;
        }
    }, { once: true });
}

function exportData() {
    const format = document.getElementById("export-select").value;
    if (!format) {
        alert("Please select a format to export.");
        return;
    }

    fetch(`/export_data?format=${format}`)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `data.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error exporting data:', error));
}