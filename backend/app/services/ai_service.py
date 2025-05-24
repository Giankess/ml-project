from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import Dict, Any, List
import json
import os
from .document_service import DocumentService

class AIService:
    def __init__(self):
        # Initialize local models using Ollama
        self.primary_model = Ollama(
            model="mistral",  # Using Mistral as primary model
            temperature=0.1
        )
        self.validation_model = Ollama(
            model="llama2",  # Using Llama 2 as validation model
            temperature=0.1
        )
        self.document_service = DocumentService()
        
        # Initialize prompts
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert legal AI assistant specializing in NDA analysis.
            Analyze the following NDA text and identify problematic clauses.
            For each problematic clause, provide:
            1. The clause text
            2. Why it's problematic
            3. A suggested improvement
            Format your response as JSON with the following structure:
            {
                "clauses": [
                    {
                        "original": "clause text",
                        "issue": "explanation of the problem",
                        "suggestion": "improved clause text"
                    }
                ]
            }"""),
            ("user", "{text}")
        ])
        
        self.validation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal validation AI assistant.
            Review the following NDA clause analysis and suggestions.
            Validate if the suggestions are legally sound and appropriate.
            Provide your feedback in JSON format:
            {
                "valid": true/false,
                "feedback": "explanation",
                "suggested_changes": {
                    "clause_id": "improved suggestion"
                }
            }"""),
            ("user", "{analysis}")
        ])

    async def analyze_document(self, document_id: str) -> Dict[str, Any]:
        """Analyze the NDA document and generate suggestions"""
        # Get document text
        doc_path = os.path.join(self.document_service.upload_dir, f"{document_id}.docx")
        with open(doc_path, "rb") as f:
            doc = Document(f)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        # Analyze document
        analysis_chain = LLMChain(llm=self.primary_model, prompt=self.analysis_prompt)
        analysis_result = await analysis_chain.arun(text=text)
        
        # Validate suggestions
        validation_chain = LLMChain(llm=self.validation_model, prompt=self.validation_prompt)
        validation_result = await validation_chain.arun(analysis=analysis_result)
        
        # Process results
        analysis_data = json.loads(analysis_result)
        validation_data = json.loads(validation_result)
        
        # Create changes dictionary for redline document
        changes = {}
        for clause in analysis_data["clauses"]:
            changes[clause["original"]] = {
                "suggestion": clause["suggestion"],
                "validated": validation_data["valid"],
                "feedback": validation_data["feedback"]
            }
        
        # Create redline document
        self.document_service.create_redline_document(document_id, changes)
        
        return {
            "document_id": document_id,
            "analysis": analysis_data,
            "validation": validation_data
        }

    async def process_feedback(self, document_id: str, feedback: str) -> Dict[str, Any]:
        """Process user feedback and generate updated suggestions"""
        feedback_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert legal AI assistant.
            Review the user feedback and previous analysis to generate improved suggestions.
            Consider the feedback carefully and provide updated suggestions that address the user's concerns.
            Format your response as JSON with the same structure as the analysis."""),
            ("user", "Previous analysis: {analysis}\nUser feedback: {feedback}")
        ])
        
        # Get previous analysis
        analysis_path = os.path.join(self.document_service.upload_dir, f"{document_id}_analysis.json")
        with open(analysis_path, "r") as f:
            previous_analysis = json.load(f)
        
        # Generate new suggestions
        feedback_chain = LLMChain(llm=self.primary_model, prompt=feedback_prompt)
        new_analysis = await feedback_chain.arun(
            analysis=json.dumps(previous_analysis),
            feedback=feedback
        )
        
        # Process new analysis
        new_analysis_data = json.loads(new_analysis)
        
        # Create updated changes dictionary
        changes = {}
        for clause in new_analysis_data["clauses"]:
            changes[clause["original"]] = {
                "suggestion": clause["suggestion"],
                "feedback": feedback
            }
        
        # Create new redline document
        self.document_service.create_redline_document(document_id, changes)
        
        return {
            "document_id": document_id,
            "new_analysis": new_analysis_data
        } 