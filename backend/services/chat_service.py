from typing import Dict, Any, List
from ..models.knowledge import Department, Program, Faculty, Building, Event, Service
from ..models.user import Conversation, Message
from .nlp_service import NLPService
from sqlalchemy.orm import Session
import json

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.nlp_service = NLPService()
        
    def process_message(self, user_id: int, message_text: str) -> Dict[str, Any]:
        """Process a user message and generate a response."""
        # Get or create conversation
        conversation = self._get_or_create_conversation(user_id)
        
        # Process the message with NLP
        nlp_result = self.nlp_service.process_message(message_text)
        
        # Update conversation context
        current_context = json.loads(conversation.context) if conversation.context else {}
        updated_context = self.nlp_service.update_context(current_context, nlp_result)
        conversation.context = json.dumps(updated_context)
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            content=message_text,
            is_user=True
        )
        self.db.add(user_message)
        
        # Generate response
        response = self._generate_response(nlp_result, updated_context)
        
        # Save bot response
        bot_message = Message(
            conversation_id=conversation.id,
            content=response["text"],
            is_user=False
        )
        self.db.add(bot_message)
        
        self.db.commit()
        
        return {
            "response": response,
            "conversation_id": conversation.id
        }
    
    def _get_or_create_conversation(self, user_id: int) -> Conversation:
        """Get the most recent active conversation or create a new one."""
        conversation = self.db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .order_by(Conversation.last_activity.desc())\
            .first()
            
        if not conversation:
            conversation = Conversation(user_id=user_id)
            self.db.add(conversation)
            self.db.commit()
            
        return conversation
    
    def _generate_response(self, nlp_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response based on the NLP results and context."""
        intent = nlp_result["intent"]["intent"]
        entities = nlp_result["entities"]["entities"]
        
        # Map intent to appropriate response generator
        response_generators = {
            "academic_info": self._generate_academic_response,
            "registration": self._generate_registration_response,
            "financial_aid": self._generate_financial_aid_response,
            "campus_location": self._generate_location_response,
            "faculty_info": self._generate_faculty_response,
            "events": self._generate_events_response,
            "student_services": self._generate_services_response,
            "housing": self._generate_housing_response
        }
        
        generator = response_generators.get(intent, self._generate_fallback_response)
        return generator(entities, context)
    
    def _generate_academic_response(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for academic information queries."""
        # Extract relevant entities
        departments = [e["word"] for e in entities if e["entity"] == "departments"]
        
        if departments:
            department = self.db.query(Department)\
                .filter(Department.name.in_(departments))\
                .first()
                
            if department:
                programs = self.db.query(Program)\
                    .filter(Program.department_id == department.id)\
                    .all()
                    
                program_list = "\n".join([f"- {p.name} ({p.degree_type})" for p in programs])
                
                return {
                    "text": f"The {department.name} department offers the following programs:\n{program_list}\n\nFor more information, visit {department.location} or contact {department.contact_info}.",
                    "type": "academic_info"
                }
        
        return {
            "text": "I can help you find information about academic programs. Could you please specify which department you're interested in?",
            "type": "clarification"
        }
    
    def _generate_registration_response(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for registration-related queries."""
        time_periods = [e["word"] for e in entities if e["entity"] == "time_periods"]
        
        if time_periods:
            return {
                "text": f"For {time_periods[0]}, registration typically opens in March for fall and October for spring. The exact dates can be found on the academic calendar. Would you like me to provide more specific information about the registration process?",
                "type": "registration_info"
            }
        
        return {
            "text": "I can help you with registration information. Are you looking for information about a specific semester or the general registration process?",
            "type": "clarification"
        }
    
    def _generate_financial_aid_response(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for financial aid queries."""
        return {
            "text": "The Financial Aid office is located in the Student Services Building. You can apply for financial aid by completing the FAFSA form. The priority deadline is typically March 1st for the following academic year. Would you like more specific information about scholarships or other financial aid options?",
            "type": "financial_aid_info"
        }
    
    def _generate_location_response(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for location queries."""
        buildings = [e["word"] for e in entities if e["entity"] == "buildings"]
        
        if buildings:
            building = self.db.query(Building)\
                .filter(Building.name.in_(buildings))\
                .first()
                
            if building:
                return {
                    "text": f"The {building.name} ({building.code}) is located at {building.location}. It is open {building.hours}.",
                    "type": "location_info"
                }
        
        return {
            "text": "I can help you find locations on campus. Could you please specify which building you're looking for?",
            "type": "clarification"
        }
    
    def _generate_faculty_response(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for faculty information queries."""
        faculty_roles = [e["word"] for e in entities if e["entity"] == "faculty_roles"]
        departments = [e["word"] for e in entities if e["entity"] == "departments"]
        
        if departments and faculty_roles:
            faculty = self.db.query(Faculty)\
                .join(Department)\
                .filter(Department.name.in_(departments))\
                .filter(Faculty.title.in_(faculty_roles))\
                .first()
                
            if faculty:
                return {
                    "text": f"{faculty.name} ({faculty.title}) can be reached at {faculty.email}. Their office is located in {faculty.office_location} and their office hours are {faculty.office_hours}.",
                    "type": "faculty_info"
                }
        
        return {
            "text": "I can help you find faculty information. Could you please specify which department and faculty member you're looking for?",
            "type": "clarification"
        }
    
    def _generate_events_response(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for events queries."""
        events = [e["word"] for e in entities if e["entity"] == "events"]
        
        if events:
            event = self.db.query(Event)\
                .filter(Event.title.in_(events))\
                .first()
                
            if event:
                return {
                    "text": f"The {event.title} will take place at {event.location} from {event.start_time} to {event.end_time}. {event.description}",
                    "type": "event_info"
                }
        
        return {
            "text": "I can help you find information about campus events. Would you like to know about upcoming events or a specific event?",
            "type": "clarification"
        }
    
    def _generate_services_response(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for student services queries."""
        services = [e["word"] for e in entities if e["entity"] == "services"]
        
        if services:
            service = self.db.query(Service)\
                .filter(Service.name.in_(services))\
                .first()
                
            if service:
                return {
                    "text": f"The {service.name} is located at {service.location}. They are open {service.hours}. {service.description} You can contact them at {service.contact_info}.",
                    "type": "service_info"
                }
        
        return {
            "text": "I can help you find information about student services. Could you please specify which service you're interested in?",
            "type": "clarification"
        }
    
    def _generate_housing_response(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for housing queries."""
        return {
            "text": "On-campus housing applications typically open in October for the following academic year. There are several residence hall options available, including traditional dorms and apartment-style living. Would you like more specific information about housing options or the application process?",
            "type": "housing_info"
        }
    
    def _generate_fallback_response(self, entities: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback response when the intent is not recognized."""
        return {
            "text": "I'm not sure I understand your question. Could you please rephrase it or provide more details? I can help you with information about academics, registration, campus locations, events, and more.",
            "type": "fallback"
        } 