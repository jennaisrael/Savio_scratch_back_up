From an email from Sam Iacobellis, SIO UCSD to me on Jan 16 2025

I have attached two gzip'd text files, one for SF and the other for Monterey.  These
contain the daily values that we used to build the regression model.  

Once gunzip'd, each line will contain data for a single day with format:

Year, Month, Day, ResWL_lo, ResWL_hi, SLPa, TASa, N34a, PDOa, U10a, V10a

ResWL_lo and ResWL_hi: these are the low-frequency and high-frequency components of the residual water level 
in units of meters.  The residual was calculated by subtracting the predicted astronomical tide from the observed
water level.  Values were averaged to form daily means and then detrended to remove the secular sea level rise.
We separated the terms into a high- and low-component as were experimenting with separate regressions for each.
Nothing came of that for this study, so to find the total residual simply add the two terms.  

For the following variables, the anomalies were calculated by removing the climatological seasonal cycle. 

SLPa: daily mean sea level pressure anomaly (hPa); time series detrended.

TASa: daily mean surface air temperature (proxy for SST) anomaly, time series detrended (degC)

N34a; daily mean SST anomaly over Nino3.4 region, detrended (degC) (values from ERSST5 data).

PDOa: daily PDO index (interpolated to daily from monthly values), anomalized (we ended up not including
PDO in our regression as we found it did not have any significant contribution). 

U10a: daily mean u-wind stress anomaly, detrended (m^2/s^2).  We used a simple formula for wind
stress of u_windstress = u * sqrt((u*u + v*v)); so no drag coef or density. 

V10a: daily mean v-wind stress anomaly, detrended (m^2/s^2).



For some reason, the ERA data we had started on 2/1/1950 instead of 1/1/1950.  Also, we removed
data during known tsunami events:

1964: Mar28 to Apr1
2010: Feb27 to Mar/2
2011: Mar11 to Mar14

I think that's it.  Please let me know if you have any questions.
