import sys
sys.path.append('/TabPy')
from geocode import geocodeReverse

def prepGeo(input):
    prepData = geocodeReverse(input)
    return prepData

def get_output_schema():
    return pd.DataFrame(
        {
            "InitialQuery": prep_string(),
            "ReturnAddress": prep_string(),
            "Accuracy": prep_string(),
            "Relevance": prep_decimal()
        }
    )