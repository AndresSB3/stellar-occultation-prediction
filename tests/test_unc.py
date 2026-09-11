import numpy as np
import pytest

from src.unc import jpl_unc, mpc_unc


# Test invalid methods
def test_jpl_unc_invalid_method():
  
  # Arbitrary uncertainty
  row = {
    "RA_3sigma": 6,
    "DEC_3sigma": 12,
  }

  # With an unknown method, we expect a value error
  with pytest.raises(ValueError):
    jpl_unc(row, method="banana")
    
def test_mpc_unc_invalid_method():

  # Arbitrary uncertainty
  row = {
    "Uncertainty 3sig": 6,
  }

  # With an unknown method, we expect a value error
  with pytest.raises(ValueError):
    mpc_unc(row, method="apple")

# Test math when using the square method for uncertainties in ephemeris
def test_jpl_unc_sqr():
  
  # Arbitrary uncertainties
  row = {
    "RA_3sigma": 6,
    "DEC_3sigma": 12,
  }
  result = jpl_unc(row, method="sqr")

  # We expect the following result
  expected = np.array([
    [4, 0],
    [0, 16],
  ])
  np.testing.assert_allclose(result, expected)
  
def test_mpc_unc_sqr():
  
  # Arbitrary uncertainties
  row = {
    "Uncertainty 3sig": 6,
  }
  result = mpc_unc(row, method="sqr")

  # We expect the following result
  expected = np.array([
    [4, 0],
    [0, 4],
  ])
  np.testing.assert_allclose(result, expected)

# Test matrix values with sqr method
def test_jpl_unc_sqr_properties():
  
  # Arbitrary uncertainties
    row = {
      "RA_3sigma": 1.25,
      "DEC_3sigma": 7.64,
    }
    covariance = jpl_unc(row, method="sqr")
    
    # The matrix must be symmetric
    assert np.allclose(covariance, covariance.T)
    
    # Variances must not be negative
    assert np.all(np.diag(covariance) >= 0)
    
def test_mpc_unc_sqr_properties():
  
  # Arbitrary uncertainties
    row = {
      "Uncertainty 3sig": 2.903,
    }
    covariance = mpc_unc(row, method="sqr")
    
    # The matrix must be symmetric
    assert np.allclose(covariance, covariance.T)
    
    # Variances must not be negative
    assert np.all(np.diag(covariance) >= 0)
    
# Test zero uncertainty with sqr method
def test_zero_uncertainty_jpl():
  row = {
    "RA_3sigma": 0,
    "DEC_3sigma": 0,
  }
  result = jpl_unc(row, method="sqr")

  # With no uncertainties, the covariance matrix must be of zeros
  assert np.array_equal(result, np.zeros((2, 2)))
  
def test_zero_uncertainty_mpc():
  row = {
    "Uncertainty 3sig": 0
  }
  result = mpc_unc(row, method="sqr")

  # With no uncertainties, the covariance matrix must be of zeros
  assert np.array_equal(result, np.zeros((2, 2)))
  
# Test math when using the covariance method for uncertainties in ephemeris
def test_jpl_unc_cov():

  # Arbitrary uncertainties (no theta)
  row = {
    'SMAA_3sigma': 6,
    'SMIA_3sigma': 3,
    'Theta_3sigma': 0
  }
  result = jpl_unc(row, method="cov")

  # We expect the following result
  expected = np.array([
    [4, 0],
    [0, 1],
  ])
  np.testing.assert_allclose(result, expected, atol=1e-12)
  
  # Add in a theta
  row['Theta_3sigma'] = 90
  result = jpl_unc(row, method="cov")
  expected = np.array([
    [1, 0],
    [0, 4],
  ])
  np.testing.assert_allclose(result, expected, atol=1e-12)
  
  # Add in an intermediate angle
  row['Theta_3sigma'] = 45
  result = jpl_unc(row, method="cov")
  expected = np.array([
    [2.5, 1.5],
    [1.5, 2.5],
  ])
  np.testing.assert_allclose(result, expected, atol=1e-12)
  
# Test matrix values using the cov method
def test_jpl_unc_cov_properties():

  # Arbitrary uncertainties
  row = {
    "SMAA_3sigma": 6,
    "SMIA_3sigma": 3,
    "Theta_3sigma": 37,
  }
  covariance = jpl_unc(row, method="cov")

  # We expect the covariance matrix to be symmetric
  assert np.allclose(covariance, covariance.T)
  
  # The eigenvalues of the covariance matrix must not be negative
  eigenvalues = np.linalg.eigvalsh(covariance)
  assert np.all(eigenvalues >= 0)
  
  # Eigenvalues must match the principal variances
  expected = np.array([1, 4])
  np.testing.assert_allclose(eigenvalues, expected)
  
  # The trace must remain constant after rotation
  assert np.isclose(np.trace(covariance), 5)