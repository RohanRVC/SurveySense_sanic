import requests

url = "http://127.0.0.1:8000/process-survey"
payload = {
    "user_id": "test_user", 
    "survey_results": [
        {"question_number": 1, "question_value": 7},
        {"question_number": 2, "question_value": 7},  
        {"question_number": 3, "question_value": 4}, 
        {"question_number": 4, "question_value": 1},
        {"question_number": 5, "question_value": 6}, 
        {"question_number": 6, "question_value": 6},
        {"question_number": 7, "question_value": 2},
        {"question_number": 8, "question_value": 7},
        {"question_number": 9, "question_value": 6},
        {"question_number": 10, "question_value": 6}
    ]
}

response = requests.post(url, json=payload)
print(response.json())
