# Stellar Ocultation Prediction Tool

Python project for the prediction of stellar occultation events. 

The project aims to develop a computational workflow for predicting stellar occultation events using stellar positions, object ephemerides and the SORA package. 

## Current Status

*Work in progress*

The project is currently under development. Current work includes:

- Input reading through a JSON file.
- Defaulting of inputs into workable hyperparameters.
- Querying and processing astronomical ephemerides from both JPL and MPC databases. 
- Basic working with uncertainties associated with object ephemerides. 

## Technologies

- Python
- Pandas
- Astropy
- Astroquery
- SORA

## Project Structure

occultations/ 
├── config/ # Settings
├── data/ # Local data
├── notebooks/ # Exploratory analysis and experiments 
├── src/ # Main project code 
├── tests/ # Automated tests 
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock

## Future Work

- Tabular ephemerides support in SORA predictions. 
- Improve uncertainty propagation.
- Add validation and automated tests. 
- Document the methodology and results.
- Complete data pipeline. 
- Stellar occultation prediction pipeline. 
- Dedicated UI.

## Author

Andrés Sánchez