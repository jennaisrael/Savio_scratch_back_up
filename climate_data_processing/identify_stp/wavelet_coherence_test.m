close all
clear
% Compute the wavelet coherence for the tide gauges and salinity at
% locations within the delta

%load point reyes tide gauge data, tidally filtered but has nans
ptr_raw=table2timetable(readtable('/global/scratch/users/jennaisrael/time_varying_data/tide_gauge_data/utide.residuals.pointreyes.1996.2021.csv'));

%load salinity data at jersey point, already gap filled and tidally
%filtered
jer=table2timetable(renamevars(readtable('/global/scratch/users/jennaisrael/climate_data_processing/identify_stp/jersey_pt_gap_filled_filtered.csv'),"value","Salinity"));

% %tidally filter the salinity data
% %use lanczos filter from matlab exchange
% %Y,coef,window,Cx,Ff] = LANCZOSFILTER(X,dT,Cf,M,pass) Filters the time
% %   series via the Lanczos filter in the frequency space (FFT), where
% %
% %   INPUTS:
% %      X    - Time series
% %      dT   - Sampling interval       (default: 1)
% %      Cf   - Cut-off frequency       (default: half Nyquist)
% %      M    - Number of coefficients  (default: 100)
% %      pass - Low or high-pass filter (default: 'low')
% %
% dT=15; %15 minute frequency data
% Cf=1/(dT*4); % half Nyquist frequency in Hz
% jer_filt=lanczosfilter(jer.value,dT,Cf,2000,'low');
% 
% figure(1)
% plot(jer.datetime,jer.value)
% hold on
% plot(jer.datetime,jer_filt)
% legend("raw","lanczos filtered (default)")

%gapfill the nontidal residual
Residual_filled=fillmissing(ptr_raw.Residual,'linear','SamplePoints',ptr_raw.DateTime);
ptr_filled=addvars(ptr_raw,Residual_filled);

ptr=timetable(ptr_filled.DateTime, ptr_filled.Residual_filled);


%resample both to be hourly
ptr_hourly=renamevars(retime(ptr, "hourly", "max"),"Var1","NTR");
jer_hourly=retime(jer,"hourly","max");
%% 

%synchonize
tt_all=synchronize(ptr_hourly,jer_hourly);

%remove the rows with missing data
tt_cleaned=rmmissing(tt_all);

%are there any gaps in time?
gapcheck=hours(diff(tt_cleaned.datetime));
figure(1)
bar(tt_cleaned.datetime(2,end),gapcheck)
%%
%frequency
f=1/3600; %hourly frequency expressed in Hertz

%need to drop the nans from the beginning and end and then identify if
%there are nans in the middle of the data and gap fill before doing wavelet
%coherence



% %Plot the signals to make sure there are not any gaps
% figure(1)
% subplot(2,1,1)
% plot(tt_cleaned.datetime,tt_cleaned.Var1)
% title('Point Reyes Elevation Residual')
% grid on
% ylabel('NTR elemation [m]')
% subplot(2,1,2)
% plot(tt_cleaned.datetime,tt_cleaned.value)
% title('Salinity at Jersey Point')
% ylabel('Salinity [PSU]')
% grid on
% xlabel('Date')

figure(2)
wcoherence(tt_all.NTR,tt_all.salinity,f)
%wcoherence(tt_cleaned.Var1,tt_cleaned.value,f)
%wcoh=wcoherence(tt_cleaned.Var1,tt_cleaned.value,f);%where Var1 is non tidal residual
%elevation in m and value is salinity at jersey point in psu


% this isn't working can't load the default data 
% try the example from the documentation first

% load wcoherdemosig1
% subplot(2,1,1)
% plot(t,x1)
% title('X Signal')
% grid on
% ylabel('Amplitude')
% subplot(2,1,1)
% plot(t,y1)
% title('Y Signal')
% ylabel('Amplitude')
% grid on
% xlabel('Seconds')
% 
% % figure
% % wcoherence(x1,y1,1000) %signal 1, signal 2, sampling frequency (1000 Hz for this example)
% 
