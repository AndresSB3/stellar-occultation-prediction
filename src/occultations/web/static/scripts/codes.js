// Get the observer codes for the selection of observatories from MPC

// Variable for codes link
const OBSERVATORY_URL = "https://ssp.imcce.fr/webservices/data/displayIAUObsCodes.php";

// Variable to save codes
let observatoryCodes = new Set();

// Add an action when testing occurs
async function loadObservatoryCodes() {

  // Variable for response
  const response = await fetch(OBSERVATORY_URL);

  // Check if the response is ok
  if (!response.ok) {
    throw new Error(`Could not load observatory codes. HTTP error! status: ${response.status}`);
  }

  // Save text from response
  const text = await response.text();

  // Save codes and names from data
  const observatories = text.split(/\r?\n/)
    .map(line => {
      const columns = line.trim().split(/\s+/);

      // Check if the line contains a valid observatory record
      if (columns.length < 5 || !/^[A-Z0-9]{3}$/.test(columns[0])) {
        return null;
      }

      return {
        code: columns[0],
        name: columns.slice(4).join(" ")
      };
    })
    .filter(Boolean);
  
  // Save valid codes
  observatoryCodes = new Set(observatories.map(obs => obs.code));

  return observatories;
};

// Populate the observatory codes select element
function populateObservatoryDropdown(observatories) {

  // Get the datalist element
  const datalist = document.querySelector('#observatory-options');

  // Remove previous options
  datalist.innerHTML = "";

  // Create options
  observatories.forEach(({code, name}) => {
    const option = document.createElement('option');
    option.value = code;
    option.label = name;
    datalist.appendChild(option);
  });
};

// Load observatory codes and populate the dropdown
document.addEventListener('DOMContentLoaded', async () => {
  try {

    // Load observatory codes and populate the dropdown}
    const observatories = await loadObservatoryCodes();
    populateObservatoryDropdown(observatories);
  } catch (error) {

    // Log the error and display a message in the dropdown
    console.error('Error loading observatory codes:', error);
    alert('Error loading observatory codes.');
  }
});