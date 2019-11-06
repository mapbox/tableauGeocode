import sys
sys.path.append('/TabPy')
from geocode import geocodeForward

def prepGeo(input):
    prepData = geocodeForward(input,"token")
    return prepData

def get_output_schema():
    return pd.DataFrame(
        {
            "InitialQuery": prep_string(),
            "ReturnAddress": prep_string(),
            "Accuracy": prep_string(),
            "Relevance": prep_decimal(),
            "Longitude": prep_decimal(),
            "Latitude": prep_decimal(),
        }
    )