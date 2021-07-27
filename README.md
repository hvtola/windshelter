# windshelter
This python script reimplements the Wind Shelter Index proposed by Plattner et al. (2004), that has originally been implemented within the RSAGA package.

See in depth description here:
https://rdrr.io/cran/RSAGA/man/wind.shelter.html

NB! The tolerance and direction works different from the RSAGA. In this python script uses a angle range instead, i.e.: 

def windshelter_prep(radius, direction, tolerance, cellsize): # 0 degrees equals East (90 degrees) for direction and tolerance.

(direction = 0, tolerance = 90) would equal the angle range from 90 degrees (east) to 180 degrees (south)

(direction = 90, tolerance = 180) would equal the angle range from 180 degrees (south) to 270 degrees (west)

(direction = 180, tolerance = 270) would equal the angle range from 270 degrees (west) to 360 degrees (north)

(direction = 270, tolerance = 360) would equal the angle range from 360 degrees (north) to 90 degrees (east)

### References:

Plattner, C., Braun, L.N., Brenning, A. (2004): Spatial variability of snow accumulation on Vernagtferner, Austrian Alps, in winter 2003/2004. Zeitschrift fuer Gletscherkunde und Glazialgeologie, 39: 43-57.

Winstral, A., Elder, K., Davis, R.E. (2002): Spatial snow modeling of wind-redistributed snow using terrain-based parameters. Journal of Hydrometeorology, 3: 524-538.
