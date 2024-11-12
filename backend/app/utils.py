from pydantic import BaseModel, ValidationError, validator
from typing import List

class SurveyResult(BaseModel):
    question_number: int
    question_value: int

    @validator("question_number")
    def validate_question_number(cls, v):
        if not 1 <= v <= 10:
            raise ValueError("question_number must be between 1 and 10.")
        return v

    @validator("question_value")
    def validate_question_value(cls, v):
        if not 1 <= v <= 7:
            raise ValueError("question_value must be between 1 and 7.")
        return v

class SurveyPayload(BaseModel):
    user_id: str
    survey_results: List[SurveyResult]

    @validator("user_id")
    def validate_user_id(cls, v):
        if not v.isalnum() or len(v) < 5:
            raise ValueError("user_id must be at least 5 characters long and alphanumeric.")
        return v

    @validator("survey_results")
    def validate_survey_results(cls, v):
        if len(v) != 10:
            raise ValueError("survey_results must contain exactly 10 items.")
        question_numbers = [item.question_number for item in v]
        if len(set(question_numbers)) != 10:
            raise ValueError("Each question_number must appear exactly once.")
        return v
