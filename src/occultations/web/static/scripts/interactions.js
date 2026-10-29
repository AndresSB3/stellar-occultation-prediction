// Get body selection element
const bodySelectionElement = document.querySelector(".js-body-selection");

// When changing the value, display the necessary elements
bodySelectionElement.onchange = () => {
  if(bodySelectionElement.value === "ids") {
    document.querySelector(".body-inputs-ids").style.display = "grid";
    document.querySelector(".body-inputs-filters").style.display = "none";
  } else if(bodySelectionElement.value === "filters"){
    document.querySelector(".body-inputs-ids").style.display = "none";
    document.querySelector(".body-inputs-filters").style.display = "grid";
  }
};

// Get epoch selection element
const epochSelectionElement = document.querySelector(".js-epoch-selection");

// When changing the value, display the necessary elements
epochSelectionElement.onchange = () => {
  if(epochSelectionElement.value == "list") {
    document.querySelector(".epoch-inputs-list").style.display = "grid";
    document.querySelector(".epoch-inputs-range").style.display = "none";
  } else if(epochSelectionElement.value == "range") {
    document.querySelector(".epoch-inputs-list").style.display = "none";
    document.querySelector(".epoch-inputs-range").style.display = "grid";
  }
};

// Get observer selection element
const observerSelectionElement = document.querySelector(".js-observer-selection");

// When changing the value, display the necessary elements
observerSelectionElement.onchange = () => {
  if(observerSelectionElement.value == "coord") {
    document.querySelector(".observer-inputs-coords").style.display = "grid";
    document.querySelector(".observer-inputs-codes").style.display = "none";
  } else if(observerSelectionElement.value == "code") {
    document.querySelector(".observer-inputs-coords").style.display = "none";
    document.querySelector(".observer-inputs-codes").style.display = "grid";
  }
};