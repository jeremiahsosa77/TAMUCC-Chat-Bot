from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..models.base import get_db
from ..services.chat_service import ChatService
from ..models.user import User
from pydantic import BaseModel

router = APIRouter()

class MessageRequest(BaseModel):
    text: str
    user_id: int

class MessageResponse(BaseModel):
    response: Dict[str, Any]
    conversation_id: int

@router.post("/message", response_model=MessageResponse)
async def process_message(
    request: MessageRequest,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """Process a user message and return a response."""
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    chat_service = ChatService(db)
    result = chat_service.process_message(request.user_id, request.text)
    
    return MessageResponse(
        response=result["response"],
        conversation_id=result["conversation_id"]
    )

@router.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get the history of a conversation."""
    from ..models.user import Conversation, Message
    
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.timestamp)\
        .all()
    
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": msg.id,
                "content": msg.content,
                "is_user": msg.is_user,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    }

@router.post("/feedback/{message_id}")
async def submit_feedback(
    message_id: int,
    rating: int,
    comment: str = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Submit feedback for a specific message."""
    from ..models.user import Message, Feedback
    
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    feedback = Feedback(
        message_id=message_id,
        rating=rating,
        comment=comment
    )
    
    db.add(feedback)
    db.commit()
    
    return {"status": "success", "message": "Feedback submitted successfully"} 