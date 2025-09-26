from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Question:
    id: int
    text: str
    category: str
    difficulty: str

@dataclass
class Response:
    question_id: int
    question: str
    category: str
    answer: str
    time_taken: float