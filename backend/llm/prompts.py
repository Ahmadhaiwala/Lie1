"""
Prompt Templates for Common Tasks
"""
from typing import Dict, Any


class PromptTemplates:
    """Collection of reusable prompt templates"""
    
    @staticmethod
    def web_content_analyzer() -> str:
        """System prompt for analyzing web content"""
        return """You are an expert web content analyzer. Your role is to:
- Extract key information from web pages
- Identify main topics and themes
- Summarize content clearly and accurately
- Recognize structured data patterns
- Understand context and relationships

Provide clear, accurate analysis based only on the provided content."""
    
    @staticmethod
    def data_extractor() -> str:
        """System prompt for data extraction"""
        return """You are a precise data extraction specialist. Your role is to:
- Extract specific data fields from unstructured content
- Follow schemas and patterns exactly
- Maintain data accuracy and integrity
- Handle missing or ambiguous data appropriately
- Return clean, structured output

Always output valid JSON matching the provided schema."""
    
    @staticmethod
    def article_summarizer() -> str:
        """System prompt for article summarization"""
        return """You are an expert at summarizing articles and content. Your summaries are:
- Clear and concise
- Capture all key points
- Maintain factual accuracy
- Well-structured and readable
- Appropriate for the target length

Focus on the most important information."""
    
    @staticmethod
    def qa_assistant() -> str:
        """System prompt for question answering"""
        return """You are a helpful Q&A assistant. You:
- Answer questions accurately based on provided context
- Cite sources when possible
- Admit when information is not available
- Provide clear, direct answers
- Explain complex topics simply

Only use information from the provided context."""
    
    @staticmethod
    def product_info_extractor() -> Dict[str, Any]:
        """Schema for extracting product information"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Product name"},
                "price": {"type": "number", "description": "Product price"},
                "currency": {"type": "string", "description": "Currency code (USD, EUR, etc)"},
                "description": {"type": "string", "description": "Product description"},
                "features": {"type": "array", "items": {"type": "string"}, "description": "Key features"},
                "availability": {"type": "string", "description": "Stock status"},
                "rating": {"type": "number", "description": "Average rating (0-5)"},
                "review_count": {"type": "integer", "description": "Number of reviews"},
                "images": {"type": "array", "items": {"type": "string"}, "description": "Image URLs"},
                "category": {"type": "string", "description": "Product category"},
            },
            "required": ["name"]
        }
    
    @staticmethod
    def article_metadata_extractor() -> Dict[str, Any]:
        """Schema for extracting article metadata"""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Article title"},
                "author": {"type": "string", "description": "Author name"},
                "publish_date": {"type": "string", "description": "Publication date (ISO format)"},
                "summary": {"type": "string", "description": "Brief summary (1-2 sentences)"},
                "main_topics": {"type": "array", "items": {"type": "string"}, "description": "Main topics covered"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Content tags"},
                "word_count": {"type": "integer", "description": "Estimated word count"},
                "read_time": {"type": "integer", "description": "Estimated read time in minutes"},
            },
            "required": ["title"]
        }
    
    @staticmethod
    def contact_info_extractor() -> Dict[str, Any]:
        """Schema for extracting contact information"""
        return {
            "type": "object",
            "properties": {
                "emails": {"type": "array", "items": {"type": "string"}, "description": "Email addresses"},
                "phones": {"type": "array", "items": {"type": "string"}, "description": "Phone numbers"},
                "addresses": {"type": "array", "items": {"type": "string"}, "description": "Physical addresses"},
                "social_media": {
                    "type": "object",
                    "properties": {
                        "twitter": {"type": "string"},
                        "facebook": {"type": "string"},
                        "linkedin": {"type": "string"},
                        "instagram": {"type": "string"},
                    }
                },
                "website": {"type": "string", "description": "Main website URL"},
            }
        }
    
    @staticmethod
    def job_posting_extractor() -> Dict[str, Any]:
        """Schema for extracting job posting information"""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Job title"},
                "company": {"type": "string", "description": "Company name"},
                "location": {"type": "string", "description": "Job location"},
                "salary_range": {"type": "string", "description": "Salary range if mentioned"},
                "job_type": {"type": "string", "description": "Full-time, part-time, contract, etc."},
                "remote": {"type": "boolean", "description": "Whether position is remote"},
                "requirements": {"type": "array", "items": {"type": "string"}, "description": "Job requirements"},
                "responsibilities": {"type": "array", "items": {"type": "string"}, "description": "Job responsibilities"},
                "benefits": {"type": "array", "items": {"type": "string"}, "description": "Benefits offered"},
                "posted_date": {"type": "string", "description": "When job was posted"},
                "application_url": {"type": "string", "description": "URL to apply"},
            },
            "required": ["title", "company"]
        }
    
    @staticmethod
    def event_info_extractor() -> Dict[str, Any]:
        """Schema for extracting event information"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Event name"},
                "date": {"type": "string", "description": "Event date"},
                "time": {"type": "string", "description": "Event time"},
                "location": {"type": "string", "description": "Event location"},
                "description": {"type": "string", "description": "Event description"},
                "organizer": {"type": "string", "description": "Event organizer"},
                "price": {"type": "string", "description": "Ticket price"},
                "registration_url": {"type": "string", "description": "Registration link"},
                "categories": {"type": "array", "items": {"type": "string"}, "description": "Event categories"},
            },
            "required": ["name", "date"]
        }
    
    @staticmethod
    def create_extraction_prompt(
        content: str,
        schema: Dict[str, Any],
        additional_instructions: str = ""
    ) -> str:
        """
        Create a prompt for structured data extraction
        
        Args:
            content: Content to extract from
            schema: JSON schema
            additional_instructions: Extra instructions
            
        Returns:
            Formatted prompt
        """
        import json
        
        prompt = f"""Extract structured data from the following content according to the schema provided.

Schema:
```json
{json.dumps(schema, indent=2)}
```

{f"Additional Instructions:\n{additional_instructions}\n" if additional_instructions else ""}

Content:
{content}

Extract the data and return it as valid JSON matching the schema above."""
        
        return prompt
