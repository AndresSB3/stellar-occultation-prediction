// Send data with FastAPI to pipeline
document.querySelector("#generate-ephemerides").addEventListener("click", async() => {

  // Save button element
  const button = document.querySelector("#generate-ephemerides");

  try {

    // Create object with inputted information
    const config = collectFormData();

    // Prevent duplicate submissions while the pipeline is running
    button.disabled = true;
    button.textContent = "Generating ephemerides...";

    // Send configuration
    const response = await fetch("/api/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(config)
    });

    // wait for the pipeline to finish
    const result = await response.json();

    // Verify request
    if (!response.ok) {
      throw new Error(result.detail || "Request failed");
    }

    console.log("Pipeline result:", result);
    alert("Ephemerides generated successfully!");
  } catch (error) {
    console.error("Error running pipeline:", error);
    alert(`Could not generate ephemerides: ${error.message}`);
  } finally {

    // Restore button
    button.disabled = false;
    button.textContent = "Generate Ephemerides";
  }
});