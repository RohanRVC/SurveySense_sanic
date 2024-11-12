
import os
from statistics import mean
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import aiofiles
import csv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set default logging level
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file named app.log
        logging.StreamHandler()          # Log to the console
    ]
)
import statistics

def calculate_statistics(question_values):
    """Calculate mean, median, and standard deviation for question values."""
    values = list(question_values.values())
    mean_value = statistics.mean(values)
    median_value = statistics.median(values)
    std_dev_value = statistics.stdev(values) if len(values) > 1 else 0  # Standard deviation requires at least 2 values
    return {
        "mean": mean_value,
        "median": median_value,
        "std_dev": std_dev_value
    }


# Define the CSV file path and headers
DATABASE_FILE = "main_data.csv"
CSV_HEADERS = ["user_id", "overall_analysis", "cat_dog", "fur_value", "tail_value", "description"]

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print(f"Loaded API Key: {GOOGLE_API_KEY}")

# Configure Gemini API
genai.configure(api_key='AIzaSyC3B0Z0hg6cZ08Jh8WP4OgsJtdfk28INcw')

# Define paths for prompt and content files
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROMPT_DIR = BASE_DIR / "prompts"
SHORT_HAIR_PATH = PROMPT_DIR / "the_value_of_short_hair.txt"
LONG_HAIR_PATH = PROMPT_DIR / "the_value_of_long_hair.txt"
SYSTEM_PROMPT_PATH = PROMPT_DIR / "system_prompt.txt"

print('Base dir:', BASE_DIR)
print('SHORT_HAIR_PATH:', SHORT_HAIR_PATH)
print('LONG_HAIR_PATH:', LONG_HAIR_PATH)
print('SYSTEM_PROMPT_PATH:', SYSTEM_PROMPT_PATH)

async def process_survey_data(payload):
    try:
        # Start processing
        logging.info("Starting survey data processing.")

        # Extract survey data
        user_id = payload.get("user_id")
        survey_results = payload.get("survey_results")

        # Validate payload
        if not user_id or not survey_results:
            logging.warning("Invalid payload structure: missing user_id or survey_results.")
            return {"error": "Invalid payload structure"}, 400

        # Extract question values and calculate the average
        question_values = {item["question_number"]: item["question_value"] for item in survey_results}
        avg_value = mean(question_values.values())

        # Process real-time rules
        overall_analysis = "unsure" if question_values[1] == 7 and question_values[4] < 3 else "certain"
        cat_dog = "cats" if question_values[10] > 5 and question_values[9] <= 5 else "dogs"
        fur_value = "long" if avg_value > 5 else "short"
        tail_value = "long" if question_values[7] > 4 else "short"

        # Generate description using Gemini API
        description = await generate_description_with_gemini(avg_value)

        # Calculate summary statistics
        statistics_summary = calculate_statistics(question_values)

        # Construct the response with statistics
        response = {
            "user_id": user_id,
            "overall_analysis": overall_analysis,
            "cat_dog": cat_dog,
            "fur_value": fur_value,
            "tail_value": tail_value,
            "description": description,
            "statistics": statistics_summary  # Adding the summary statistics to the response
        }

        # Save the response to CSV
        await async_save_survey_result(response)

        return response, 200  # Successful response

    except ValueError as ve:
        # Handle validation errors specifically
        logging.error(f"Validation error: {ve}")
        return {"error": str(ve)}, 400

    except Exception as e:
        # Catch any unexpected errors
        logging.error(f"Unexpected error in process_survey_data: {e}")
        return {"error": "Internal Server Error"}, 500


async def generate_description_with_gemini(avg_value):
    """Generate a description based on the average value using the Gemini API."""
    try:
        # Select the appropriate content file based on average value
        content_file = SHORT_HAIR_PATH if avg_value > 4 else LONG_HAIR_PATH
        with open(content_file, "r") as file:
            content = file.read()

        # Load the system prompt
        with open(SYSTEM_PROMPT_PATH, "r") as file:
            system_prompt = file.read()

        # Use the Gemini API to generate content
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"{system_prompt}\n\n{content}"
        
        response = model.generate_content(prompt)

        # Clean the description by removing newlines if any
        description = response.text.replace('\n', ' ').replace(',', ' ') if response else "Default description"
        return description

    except FileNotFoundError as e:
        return "Default description due to missing file"
    except Exception as e:
        return "Default description due to API error"


async def async_save_survey_result(record):
    """Asynchronously saves a survey result to a CSV file."""
    file_exists = os.path.isfile(DATABASE_FILE)

    # Clean the description field to remove newlines
    record["description"] = record["description"].replace('\n', ' ')
    
    # Flatten statistics for easier CSV storage
    record["mean"] = record["statistics"]["mean"]
    record["median"] = record["statistics"]["median"]
    record["std_dev"] = record["statistics"]["std_dev"]
    del record["statistics"]  # Remove nested statistics to simplify CSV storage

    # Update CSV headers to include new fields if not already present
    extended_headers = CSV_HEADERS + ["mean", "median", "std_dev"]

    # Open the CSV file in append mode and write the record
    async with aiofiles.open(DATABASE_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=extended_headers)

        # Write headers only if the file is new
        if not file_exists:
            await f.write(",".join(extended_headers) + "\n")

        # Write the record as a row in the CSV file
        await f.write(",".join(str(record.get(header, "")) for header in extended_headers) + "\n")
        print("Survey result saved successfully to CSV.")


async def async_load_survey_results():
    """Asynchronously loads all survey results from a CSV file."""
    records = []

    # Check if the CSV file exists
    if not os.path.isfile(DATABASE_FILE):
        print("No data found.")
        return records

    # Open the CSV file and read the records
    async with aiofiles.open(DATABASE_FILE, "r") as f:
        async for line in f:
            # Skip the header line
            if line.startswith(CSV_HEADERS[0]):
                continue

            # Parse each line into a dictionary based on CSV headers
            values = line.strip().split(",")
            record = {CSV_HEADERS[i]: values[i] for i in range(len(CSV_HEADERS))}
            records.append(record)

    print("Survey results loaded successfully from CSV.")
    return records
