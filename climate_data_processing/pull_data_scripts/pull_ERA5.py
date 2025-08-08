import cdsapi

dataset = "reanalysis-era5-single-levels-timeseries"
request = {
    "location": {"longitude": -122.000000, "latitude": 36.500000},
    #"location": {"longitude": -121.891667, "latitude": 36.6083},
    #"location": {"longitude": -122.967778, "latitude": 37.985278},#point reyes
    "date": ["1970-01-01/2025-01-01"]
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
