from astroquery.mpc import MPC

def ephemerides(id, start, step, num, obs=None):
  if obs:
    return MPC.get_ephemeris(id, start=start, step=step, number=num, location=obs)
  return MPC.get_ephemeris(id, start=start, step=step, number=num)