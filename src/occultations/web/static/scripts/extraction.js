// Function to get body data
function collectBodyData(bodyMode) {
  
  // Create body object depending on selection
  const body = bodyMode === "ids" 
    ? {
      id: getWrittenValues(".body-ids"),
      fields: null
    } 
    : {
      id: null,
      fields: {
        object_type: getSelectedValues(".body-type"),
        family: getSelectedValues(".body-family"),
        state: getSelectedValues(".body-status"),
        orbit_uncertainty: getSelectedValues(".body-uncertainty"),
        limit: getNumber(".body-limit")
      }
    };
  return body;
}

// Function to get epoch data
function collectEpochData(epochMode) {

  // Create epoch object depending on selection
  let epoch;
  if (epochMode === "range") {
    const epochStart = document.querySelector("#epoch-start").value;
    const epochStop = document.querySelector("#epoch-stop").value;
    const epochStepValue = document.querySelector("#epoch-step").value;

    const allEpochEmpty = !epochStart && !epochStop && !epochStepValue;
    const someEpochEmpty = !epochStart || !epochStop || !epochStepValue;

    if (allEpochEmpty) {
      epoch = null;
    } else if (someEpochEmpty) {
      throw new Error("Please complete all epoch fields.");
    } else {
      epoch = {
        start: epochStart,
        stop: epochStop,
        step: getDateStep(),
        number: computeDateDifference()
      };
    }
  } else {
    epoch = getWrittenValues(".epoch-list");
  };
  return epoch;
}

// Function to collect observer data
function collectObserverData(observerMode) {

  // Create observer object depending on selection

  // Case code just get value from select
  if (observerMode === "code") {
    const code = document.querySelector(".observer-codes").value.trim();

    if (!code) return null;

    if (!observatoryCodes.has(code)) {
      throw new Error(`Invalid observatory code: ${code}`);
    }

    return [code];
  }

  // Case coordinates just get values from input fields
  if (observerMode === "coord") {

    // Get coordinates
    const lat = getNumber(".observer-latitude");
    const lon = getNumber(".observer-longitude");
    const alt = getNumber(".observer-altitude");

    // Check emptiness
    const allEmpty = lat === null && lon === null && alt === null;
    const someEmpty = lat === null || lon === null || alt === null;

    // No coords
    if (allEmpty) return null;

    // Some coords empty
    if (someEmpty) {
      throw new Error("Please complete all observer fields.");
    }

    // All coords available

    // Validate geographic coordinates
    if (lon < -180 || lon > 180) {
      throw new Error(`Longitude must be between -180° and 180°.`);
    }
    if (lat < -90 || lat > 90) {
      throw new Error(`Latitude must be between -90° and 90°.`);
    }
    if (alt < -1 || alt > 10) {
      throw new Error(`Elevation must be between -1 and 10 km.`);
    }

    // Return observer as an object
    return [{
      lon: lon,
      lat: lat,
      elevation: alt
    }];
  }

  // Case multiple just get values depending on each line
  if (observerMode === "multiple") {
    const text = document.querySelector(".observer-multiple").value;
    return parseObservers(text);
  }
}

// Build javascript object using the users inputs
function collectFormData() {

  // Get all selection values
  const bodyMode = bodySelectionElement.value;
  const epochMode = epochSelectionElement.value;
  const observerMode = observerSelectionElement.value;

  // Data values
  let body, epoch, observer, database;

  // Get body data
  try {
    body = collectBodyData(bodyMode);
  } catch (error) {
    alert(`Error collecting body data: ${error.message}`);
    return;
  }

  // Get epoch data
  try {
    epoch = collectEpochData(epochMode);
  } catch (error) {
    alert(`Error collecting epoch data: ${error.message}`);
    return;
  }
  
  // Get observer data
  try {
    observer = collectObserverData(observerMode);
  } catch (error) {
    alert(`Error collecting observer data: ${error.message}`);
    return;
  }

  // Create database object
  try {
    database = getSelectedValues(".databases");
  } catch (error) {
    alert(`Error collecting database data: ${error.message}`);
    return;
  }
  
  // Return object
  return {
    body: body,
    database: database,
    epoch: epoch,
    observer: observer,
    limit_magnitude: getNumber(".limit-magnitude"),
    exposition_time: getNumber(".exposition-time"),
    ADS_key: document.querySelector(".ads-key").value.trim() || null
  };
}