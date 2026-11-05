// Build javascript object using the users inputs
function collectFormData() {

  // Get all selection values
  const bodyMode = bodySelectionElement.value;
  const epochMode = epochSelectionElement.value;
  const observerMode = observerSelectionElement.value;

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
      alert("Please complete all epoch fields.");
      return;
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

  // Create observer object depending on selection
  let observer;
  if (observerMode === "coord") {

    // Get inputs
    const observerLatitude = getNumber(".observer-latitude");
    const observerLongitude = getNumber(".observer-longitude");
    const observerAltitude = getNumber(".observer-altitude");

    // Verify nulls
    const allObserverEmpty = observerLatitude == null && observerLongitude == null && observerAltitude == null;
    const someObserverEmpty = observerLatitude == null || observerLongitude == null || observerAltitude == null;

    if (allObserverEmpty) {
      observer = {
        code: null,
        coord: null
      };
    } else if(someObserverEmpty) {
      alert("Please complete all observer fields.");
      return;
    } else {
      observer = {
        code: null,
        coord: {
          lat: observerLatitude,
          lon: observerLongitude,
          elevation: observerAltitude
        }
      };
    }
  } else {
    observer = {
      code: getWrittenValues(".observer-codes"),
      coord: null 
    }
  };

  // Create databse object
  const database = getSelectedValues(".databases");

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