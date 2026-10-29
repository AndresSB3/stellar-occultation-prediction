// Get values of selected options from selection elements ignoring blank options
function getSelectedValues(selector) {
  values = [...document.querySelector(selector).selectedOptions].map(option => option.value).filter(value => value !== "");
  return values.length !== 0 ? values : null;
}

// Get values of textareas 
function getWrittenValues(selector) {

  // Make a list with the written values
  const values = document.querySelector(selector).value
    .split(/\r?\n/)                                     // split in newlines
    .map(value => value.trim())                         // to each value get rid of spaces at start and end
    .filter(value => value !== "");                     // remove empty values

  // Return list if not empty, else, return null  
  return values.length !== 0 ? values : null;
}

// Convert a numeric field to a number, or null if empty
function getNumber(selector) {
  const value = document.querySelector(selector).value.trim();

  if (value === "") {
    return null;
  }

  const number = Number(value);

  return Number.isFinite(number) ? number : null;
}

// Get step
function getDateStep() {
  const stepValue = document.querySelector("#epoch-step").value;
  const stepUnit = document.querySelector(".epoch-step-units").value;
  return stepValue !== "" ? `${stepValue}${stepUnit}` : null;
}

// Compute number of dates from start to end
function computeDateDifference() {

  // Extract dates and step
  const start = document.querySelector("#epoch-start").value;
  const stop = document.querySelector("#epoch-stop").value;
  const step = Number(document.querySelector("#epoch-step").value);

  // Verify dates
  if (!start || !stop)
    return null;

  // Verify step
  if (!Number.isFinite(step) || step <= 0)
    return null;

  // Convert dates to date objects
  const dateStart = new Date(start);
  const dateStop = new Date(stop);

  // Compute difference in miliseconds
  const dateDifference = (dateStop - dateStart);

  // Verify date order
  if (dateDifference < 0)
    return null

  // Convert to selected units
  const units = document.querySelector(".epoch-step-units").value;
  switch (units) {
    case "s":
      conversionFactor = 1000;
      break;
    case "min":
      conversionFactor = 1000 * 60; 
      break;
    case "h":
      conversionFactor = 1000 * 60 * 60;
      break;
    case "day":
      conversionFactor = 1000 * 60 * 60 * 24;
      break;
    default:
      return null;
  }
  const difference = dateDifference / conversionFactor;

  // Return difference based on the given step (including the first date)
  return Math.floor(difference / step) + 1;
}