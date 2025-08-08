import cdsapi

dataset = "reanalysis-era5-single-levels-timeseries"
request = {
    "variable": [
        "2m_dewpoint_temperature",
        "2m_temperature",
        "total_precipitation",
        "mean_sea_level_pressure",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "surface_pressure",
        "sea_surface_temperature",
        "mean_wave_direction",
        "mean_wave_period",
        "significant_height_of_combined_wind_waves_and_swell"
    ],
    "location": {"longitude": -122.25, "latitude": 36.5},
    "date": ["1970-01-01/2025-01-01"],
    "data_format": "csv"
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
