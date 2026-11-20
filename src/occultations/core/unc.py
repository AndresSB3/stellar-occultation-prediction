import numpy as np
from sora.star import Star


# Function to compute the covariance matrix of the object ephemerides from JPL Horizons
def jpl_unc(err_row, method="sqr"):
  match method:
    case "sqr":
      ra_var = (err_row['RA_3sigma'] / 3) ** 2
      dec_var = (err_row['DEC_3sigma'] / 3) ** 2
      return np.diag([ra_var, dec_var])
    case "cov":
      smaa_var = (err_row['SMAA_3sigma'] / 3) ** 2
      smia_var = (err_row['SMIA_3sigma'] / 3) ** 2
      theta = np.deg2rad(err_row['Theta_3sigma'])
      mat = np.diag([smaa_var, smia_var])
      rot = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
      ])
      return rot @ mat @ rot.T
    case _:
      raise ValueError(f"Unknown uncertainty method: {method}")

# Function to compute the covariance matrix of the object ephemerides from MPC MPES
def mpc_unc(err_row, method="sqr"):
  match method:
    case "sqr":
      var = (err_row['Uncertainty 3sig'] / 3) ** 2
      return np.diag([var, var])
    case "cov":
      var = (err_row['Uncertainty 3sig'] / 3) ** 2
      theta = np.deg2rad(90 - err_row['Unc. P.A.']) # The angle is measured from north to east, therefore we must use the complement
      mat = np.diag([var, var])
      rot = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
      ])
      return rot @ mat @ rot.T
    case _:
      raise ValueError(f"Unknown uncertainty method: {method}")
    
# Function to compute the covariance matrix of the star position from Gaia DR3 and DR4
def star_unc(star_id, epoch, method="DR3"):
  match method:
    case "DR3":
      star = Star(code=star_id, epoch=epoch)
      return star.cov[0:2, 0:2]
    case "DR4":
      pass
    
# Function to propagate the covariance matrix of both the object ephemerides and the star position into the event ephemerides
def occ_unc(body_cov, star_cov):
  
  # The covariance matrix of the event corresponds to the difference between the covariance matrices of the object ephemerides and the star position
  coef = np.array([[1, 0, -1, 0],
                   [0, 1, 0, -1]])
  
  # As the position of the star does not depend on the position of the object and viceversa, the previous matrix must multiply a diagonal matrix whose diagonal corresponds to the covariance matrix elements of both the object ephemerides and the star position
  event_cov = np.zeros((4,4))
  event_cov[0:2, 0:2] = body_cov
  event_cov[2:4, 2:4] = star_cov
  
  # The occultation covariance matrix is therefore the matricial multiplication of the coeficients (representing the difference), the diagonal matrix from above and the transposed coeficient matrix from above
  return coef @ event_cov @ coef.T
  
def event_unc(occ_cov):
  pass