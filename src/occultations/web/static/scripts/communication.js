// Send data with FastAPI to pipeline
document.querySelector("#generate-ephemerides").addEventListener("click", async() => {
  try {

    // Create object with inputted information
    const config = collectFormData();

    // Send information
    const response = await fetch("/api/config", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(config)
    });
    const result = await response.json();

    // Verify request
    if (!response.ok) {
      throw new Error(result.detail || "Request failed");
    }
    console.log("FastAPI received:", result);
    alert("Python received the configuration!");
  } catch (error) {
    console.error("Error sending configuration:", error);
    alert("Could not send the configuration to FastAPI.");
  }
});