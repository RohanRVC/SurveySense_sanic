from sanic import Blueprint, response
from backend.app.services import process_survey_data

# Define the Blueprint for your application
bp = Blueprint("survey", url_prefix="/")

# POST route to process survey data
@bp.post("process-survey")
async def process_survey_post(request):
    try:
        data = request.json  # Get the JSON payload
        result = await process_survey_data(data)  # Call the service to process data
        return response.json(result, status=200)  # Return the processed data
    except ValueError as e:
        return response.json({"error": str(e)}, status=400)  # Handle validation errors
    except Exception as e:
        return response.json({"error": "Internal Server Error"}, status=500)  # Handle generic errors

# GET route for /process-survey to return a helpful message
@bp.get("process-survey")
async def process_survey_get(request):
    return response.json({"message": "This endpoint only accepts POST requests for processing survey data."})

# Health-check route for testing if the server is running
@bp.get("health")
async def health_check(request):
    return response.json({"status": "OK", "message": "Server is running."})

# Function to set up routes in the application
def setup_routes(app):
    app.blueprint(bp)
