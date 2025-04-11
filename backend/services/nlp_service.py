from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, Any
import json
from pathlib import Path

class NLPService:
    def __init__(self):
        # Initialize the intent classification model
        self.intent_classifier = pipeline(
            "text-classification",
            model="distilbert-base-uncased",
            tokenizer="distilbert-base-uncased"
        )
        
        # Initialize the entity recognition model
        self.ner_model = pipeline(
            "ner",
            model="dbmdz/bert-large-cased-finetuned-conll03-english",
            tokenizer="dbmdz/bert-large-cased-finetuned-conll03-english"
        )
        
        # Load university-specific intents and entities
        self.intents = self._load_intents()
        self.entities = self._load_entities()
        
    def _load_intents(self) -> Dict[str, Any]:
        # Load intents from a JSON file
        intents_path = Path(__file__).parent.parent / "data" / "intents.json"
        if intents_path.exists():
            with open(intents_path, "r") as f:
                return json.load(f)
        return {}
    
    def _load_entities(self) -> Dict[str, Any]:
        # Load entities from a JSON file
        entities_path = Path(__file__).parent.parent / "data" / "entities.json"
        if entities_path.exists():
            with open(entities_path, "r") as f:
                return json.load(f)
        return {}
    
    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Classify the intent of the user's message."""
        result = self.intent_classifier(text)[0]
        return {
            "intent": result["label"],
            "confidence": result["score"]
        }
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract relevant entities from the user's message."""
        entities = self.ner_model(text)
        return {
            "entities": entities,
            "text": text
        }
    
    def process_message(self, text: str) -> Dict[str, Any]:
        """Process a user message and return intent and entities."""
        intent_result = self.classify_intent(text)
        entity_result = self.extract_entities(text)
        
        return {
            "intent": intent_result,
            "entities": entity_result,
            "original_text": text
        }
    
    def update_context(self, current_context: Dict[str, Any], new_info: Dict[str, Any]) -> Dict[str, Any]:
        """Update the conversation context with new information."""
        if not current_context:
            current_context = {
                "intent_history": [],
                "entity_history": [],
                "current_intent": None,
                "current_entities": None
            }
        
        current_context["intent_history"].append(new_info["intent"])
        current_context["entity_history"].append(new_info["entities"])
        current_context["current_intent"] = new_info["intent"]
        current_context["current_entities"] = new_info["entities"]
        
        # Keep only the last 5 turns of context
        if len(current_context["intent_history"]) > 5:
            current_context["intent_history"] = current_context["intent_history"][-5:]
            current_context["entity_history"] = current_context["entity_history"][-5:]
        
        return current_context 