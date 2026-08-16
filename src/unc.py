import numpy as np


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

def mpc_unc(err_row, method="sqr"):
  match method:
    case "sqr":
      var = (err_row['Uncertainty 3sig'] / 3) ** 2
      return np.diag([var, var])