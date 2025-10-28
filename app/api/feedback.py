
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class FeedbackRequest(BaseModel):
    name: str
    rating: int
    comments: str

@router.post("/")
def submit_feedback(req: FeedbackRequest):
    return {"message": "Feedback received", "data": req.model_dump()}
