// Get execution identifier from the URL
const params = new URLSearchParams(window.location.search);
const runId = params.get("run_id");

// Save HTML elements
const statusElement = document.querySelector("#status");
const resultsConatiner = document.querySelector("#results-container");

// Verify execution identifier
if (!runId || runId === "pending") {
  statusElement.textContent = "Invalid execution identifier.";
  statusElement.classList.add("error-message");
} else {

  // Connect to the server using Server-Sent Events
  const eventSource = new EventSource(
    `/api/runs/${encodeURIComponent(runId)}/events`
  );

  // Update status
  statusElement.textContent = "Waiting for predictions...";

  // Function to create a prediction table
  function createPredictionTable(prediction) {

    // Create container for this object-observer combination
    const card = document.createElement("article");
    card.className = "prediction-card";

    // Object heading
    const title = document.createElement("h2");
    title.textContent = prediction.object;

    // Observer heading
    const subtitle = document.createElement("h3");
    subtitle.textContent = `Observer: ${prediction.observer}`;

    // Add object and observer to card
    card.appendChild(title);
    card.appendChild(subtitle);

    // If no predictions are found, include a message and return
    if (prediction.events.length === 0) { 
      const message = document.createElement("p");
      message.className = "empty-message";
      message.textContent = "No occultaiton events found.";

      card.appendChild(message)

      return card;
    }

    // If predictions were found, create the table
    const table = document.createElement("table");

    // Headers
    const headers = [
      "Gaia DR3 Source ID",
      "Epoch (UTC)",
      "C/A (arcsec)",
      "P/A (deg)",
      "Vel (km/s)",
      "G (mag)"
    ];
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    headers.forEach(header => {
      const th = document.createElement("th");
      th.textContent = header;
      headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body
    const tbody = document.createElement("tbody");
    prediction.events.forEach(event => {
      const row = document.createElement("tr");
      const values = [
        event.star_id,
        event.epoch,
        formatNumber(event.ca, 6),
        formatNumber(event.pa, 4),
        formatNumber(event.vel, 4),
        formatNumber(event.g, 3)
      ];
      values.forEach(value => {
        const td = documento.createElement("td");
        td.textContent = value;
        row.appendChild(td);
      });

      // Keep event id available for detail tab
      row.dataset.eventId = event.eventid;
      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    card.appendChild(table);

    return card;
  }

  // Format numerical values for display
  function formatNumber(value, decimals) {
    if (value === null || value === undefined) {
      return "—";
    }

    return Number(value).toFixed(decimals);
  }

  // Listen for new predictions
  eventSource.addEventListener("prediction", event => {
    console.log("Prediction received:", event.data);
    try {
      const prediction = JSON.parse(event.data);

      // Create and display prediction table
      const card = createPredictionTable(prediction);

      resultsContainer.appendChild(card);

      statusElement.textContent = "Receiving predictions...";
    } catch (error) {
      console.error("Error displaying prediction:", error);
      statusElement.textContent = "Error displaying a prediction.";
      statusElement.classList.add("error-message");
    }
  });

  // Listen for pipeline completion
  eventSource.addEventListener("complete", event => {
    const result = JSON.parse(event.data);
    console.log("Pipeline completed:", result);
    statusElement.textContent = result.message;
    statusElement.classList.add("success-message");
    eventSource.close();
  });

  // Listen for pipeline errors
  eventSource.addEventListener("error", event => {

    // An SSE connection error does not necessarily mean that the pipeline itself failed.
    if (!event.data) {
      console.warn("SSE connection interrupted.");
      statusElement.textContent = "Connection interrupted. Trying to reconnect...";
      return;
    }
    const result = JSON.parse(event.data);
    console.error("Pipeline error:", result.message);
    statusElement.textContent = `Pipeline error: ${result.message}`;
    statusElement.classList.add("error-message");
    eventSource.close();
  });
}