// Send data with FastAPI to pipeline
document.querySelector("#generate-ephemerides").addEventListener("click", async() => {

  // Save button element
  const button = document.querySelector("#generate-ephemerides");

  // Open results tab immediately to avoid popup blockers
  const resultsTab = window.open(
    "/static/results.html?run_id=pending",
    "_blank"
  );

  // Verify that the browser allowed the new tab
  if (!resultsTab) {
    alert("Please allow pop-ups to open the results page.");
    return;
  }

  try {

    // Create object with inputted information
    const config = collectFormData();

    // Prevent duplicate submissions while the pipeline is running
    button.disabled = true;
    button.textContent = "Generating ephemerides...";

    // Send configuration and start pipeline
    const response = await fetch("/api/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(config)
    });

    // wait for the pipeline to finish
    const result = await response.json();

    console.log("HTTP status:", response.status);
    console.log("Server response:", result);

    // Verify request
    if (!response.ok) {
      throw new Error(result.detail || "Request failed");
    }

    // Change the link of the new tab using the run id of the response
    resultsTab.location.href = `/static/results.html?run_id=${encodeURIComponent(result.run_id)}`;

    console.log("Pipeline started:", result.run_id);
    
  } catch (error) {
    console.error("Error running pipeline:", error);
    alert(`Could not generate ephemerides: ${error.message}`);
  } finally {

    // Restore button
    button.disabled = false;
    button.textContent = "Generate Ephemerides";
  }
});