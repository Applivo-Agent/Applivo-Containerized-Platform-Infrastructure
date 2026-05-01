"""
app/services/resume_parser.py
────────────────────────────
Resume PDF Parser & Structured Data Extraction
- Extracts text from PDF using pdfplumber
- Parses structured data using Groq/Gemini LLM
- Returns JSON with: name, email, phone, education, experience, skills, etc.
"""

import json
import pdfplumber
import structlog
from typing import Optional, Dict, Any, List
from pathlib import Path
import re

from app.services.ai_router import AIRouter
from app.core.config import settings

logger = structlog.get_logger()

# LLM parsing prompt - VERY SIMPLE to avoid LLM confusion
RESUME_PARSING_PROMPT = """Extract resume data and return ONLY this exact JSON format:
{{
  "name": null,
  "email": null,
  "phone": null,
  "location": null,
  "professional_summary": null,
  "career_goals": null,
  "unique_value_proposition": null,
  "education": [
    {{
      "institution": "Full name of university/school",
      "degree": "Degree name (e.g., B.Tech, M.S.)",
      "field": "Field of study (e.g., Computer Science)",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM (This will be used as graduation year)",
      "gpa": "CGPA or Grade (e.g. 9.35)",
      "description": "Optional details/honors"
    }
  ],
    "work_experience": [
        {
            "title": "Job title",
            "company": "Company/Organization name",
            "location": "City/Country if available",
            "start_date": "YYYY-MM",
            "end_date": "YYYY-MM or Present",
            "is_current": false,
            "description": "Role summary",
            "bullets": ["Achievement/responsibility 1", "Achievement/responsibility 2"]
        }
    ],
  "skills": [
      "Individual Skill 1", 
      "Individual Skill 2 (NO category blocks, just the tool names)"
  ],
  "projects": [
    {
      "title": "Project Name",
      "date": "YYYY-MM",
      "description": "Summary",
      "link": "URL if any"
    }
  ],
  "awards": [
    {
      "title": "Award Title",
      "date": "YYYY-MM",
      "description": "Context"
    }
  ],
  "certifications": [],
  "linkedin_url": null,
  "github_url": null,
  "portfolio_url": null
}

SPECIFIC INSTRUCTIONS:
1. DATES: Use the format "YYYY-MM" (e.g., "2023-01") whenever possible. Use "Present" for current roles. If only the year is available, use "YYYY-01".
2. EDUCATION: If multiple degrees are listed for the SAME institution, create SEPARATE entries for each degree.
3. WORK EXPERIENCE: Extract all roles from the Experience section (full-time, part-time, internship, research). Put each role as a separate object in "work_experience".
4. SKILLS: Extract ALL technical and soft skills, even if they are categorized (e.g., 'Programming: Python, C++' should result in ['Python', 'C++']).
5. AWARDS: Include hackathon wins, honors, and scholarships in the 'awards' section.

RESUME:
__RESUME_TEXT__

Extract all available information from the resume and fill in the JSON. Keep fields null if not found. Return ONLY the JSON object, nothing else."""


class ResumeParser:
    """Parse PDF resumes and extract structured data."""

    def __init__(self):
        self.ai_router = AIRouter()

    async def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a PDF resume and extract structured data.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dict with parsed resume data
        """
        try:
            # Extract text from PDF
            resume_text = self._extract_text_from_pdf(file_path)
            
            if not resume_text or len(resume_text.strip()) < 50:
                logger.warning("resume_parse_failed", reason="insufficient_text")
                return {
                    "success": False,
                    "error": "Could not extract text from PDF. Please ensure the PDF is not scanned or corrupted.",
                }
            
            logger.info("resume_text_extracted", char_count=len(resume_text))
            
            # Parse with LLM
            parsed_data = await self._parse_with_llm(resume_text)
            
            # If LLM fails, try simple fallback extraction
            if not parsed_data.get("success"):
                logger.warning("llm_parsing_failed_trying_fallback")
                parsed_data = self._fallback_extract(resume_text)
            
            if parsed_data.get("success"):
                logger.info("resume_parse_success", fields_extracted=len(parsed_data.get("data", {})))
            
            return parsed_data
            
        except Exception as e:
            logger.error("resume_parse_error", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": f"Failed to parse resume: {str(e)}",
            }

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using pdfplumber."""
        try:
            text = []
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                    
                    logger.debug("pdf_page_extracted", page=page_num, char_count=len(page_text or ""))
            
            return "\n".join(text)
        except Exception as e:
            logger.error("pdf_extraction_error", error=str(e))
            raise

    async def _parse_with_llm(self, resume_text: str) -> Dict[str, Any]:
        """Parse extracted resume text using LLM."""
        try:
            # Use explicit token replacement instead of str.format so JSON braces in
            # the prompt template can never break interpolation.
            prompt = RESUME_PARSING_PROMPT.replace("__RESUME_TEXT__", resume_text)
            
            # Call AI router (Groq primary, Gemini fallback)
            response = await self.ai_router.chat_completions_create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a JSON API. Return ONLY valid JSON. No markdown, no explanations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=settings.OPENAI_MODEL_LIGHT,
                max_tokens=2000,
                temperature=0.0,  # Absolute zero for consistency
            )
            
            # Extract JSON from response
            response_text = (response.get("content") or "").strip()
            logger.info("llm_response_received", length=len(response_text), first_100=response_text[:100])
            
            # Try multiple strategies to extract JSON
            parsed_json = self._extract_json(response_text)
            
            # Validate and clean the parsed data
            cleaned_data = self._clean_parsed_data(parsed_json)
            
            return {
                "success": True,
                "data": cleaned_data,
            }
            
        except json.JSONDecodeError as e:
            logger.error("json_parse_error", error=str(e), response_preview=response_text[:300] if 'response_text' in locals() else "N/A")
            return {
                "success": False,
                "error": f"Failed to parse resume data. The resume format may be unusual.",
            }
        except Exception as e:
            logger.error("llm_parse_error", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": f"Failed to parse with LLM: {str(e)}",
            }

    def _extract_json(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response using multiple strategies.
        Handles markdown code blocks, extra text, etc.
        """
        # Strategy 0: Clean common artifacts
        cleaned = response_text.replace('```json', '').replace('```', '').strip()
        
        # Strategy 1: Try direct parsing (already stripped)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.debug("strategy_1_failed", error=str(e))
        
        # Strategy 2: Find JSON object by first { and last }
        try:
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_text = cleaned[start_idx:end_idx+1]
                logger.debug("strategy_2_extracted", length=len(json_text))
                return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.debug("strategy_2_failed", error=str(e))
        
        # Strategy 3: Try with relaxed parsing (remove trailing commas, etc)
        try:
            # Remove trailing commas before closing brackets
            relaxed = re.sub(r',(\s*[}\]])', r'\1', cleaned)
            return json.loads(relaxed)
        except json.JSONDecodeError as e:
            logger.debug("strategy_3_failed", error=str(e))
        
        # Strategy 4: Try to find and extract just the data inside outer braces
        try:
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            if start_idx != -1 and end_idx != -1:
                # Try progressively
                for end in range(end_idx, start_idx, -1):
                    try:
                        json_text = cleaned[start_idx:end+1]
                        result = json.loads(json_text)
                        logger.info("strategy_4_success", end_pos=end)
                        return result
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.debug("strategy_4_failed", error=str(e))
        
        # If all strategies fail, return the cleaned response with helpful error
        logger.error("json_extraction_failed", response_length=len(cleaned), first_200=cleaned[:200])
        raise json.JSONDecodeError(
            f"Could not extract valid JSON from response",
            cleaned[:500],
            0
        )

    def _fallback_extract(self, resume_text: str) -> Dict[str, Any]:
        """
        Fallback extraction using regex patterns.
        Extracts basic information when LLM parsing fails.
        """
        try:
            data = {
                "name": None,
                "email": None,
                "phone": None,
                "location": None,
                "professional_summary": None,
                "career_goals": None,
                "unique_value_proposition": None,
                "education": [],
                "work_experience": [],
                "skills": [],
                "projects": [],
                "certifications": [],
                "linkedin_url": None,
                "github_url": None,
                "portfolio_url": None,
            }
            
            # Extract email
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
            if email_match:
                data["email"] = email_match.group(0)
            
            # Extract phone (various formats)
            phone_match = re.search(r'(?:\+\d{1,3}[-.\s]?)?\(?(?:\d{3})\)?[-.\s]?(?:\d{3})[-.\s]?(?:\d{4})', resume_text)
            if phone_match:
                data["phone"] = phone_match.group(0).strip()
            
            # Extract GitHub URL
            github_match = re.search(r'https?://(?:www\.)?github\.com/[\w-]+', resume_text, re.IGNORECASE)
            if github_match:
                data["github_url"] = github_match.group(0)
            
            # Extract LinkedIn URL
            linkedin_match = re.search(r'https?://(?:www\.)?linkedin\.com/(?:in|company)/[\w-]+', resume_text, re.IGNORECASE)
            if linkedin_match:
                data["linkedin_url"] = linkedin_match.group(0)
            
            # Extract skills (look for "Skills" section)
            skills_match = re.search(r'(?:Skills?|Expertise|Technologies?)[\s:]*\n([\s\S]*?)(?:\n\n|$)', resume_text, re.IGNORECASE)
            if skills_match:
                skills_text = skills_match.group(1)
                # Split by common delimiters
                skills_list = re.split(r'[,•\n]', skills_text)
                data["skills"] = [
                    {"name": s.strip(), "category": "programming", "proficiency": "intermediate", "years_experience": 1}
                    for s in skills_list if s.strip() and len(s.strip()) > 2
                ][:20]  # Limit to 20 skills
            
            logger.info("fallback_extraction_complete", name=data.get("name"), email=data.get("email"))
            return {
                "success": True,
                "data": data,
            }
        except Exception as e:
            logger.error("fallback_extraction_failed", error=str(e))
            return {
                "success": False,
                "error": "Could not extract resume data using fallback method.",
            }

    def _clean_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate parsed resume data."""
        cleaned = {}
        
        # String fields
        for field in ["name", "email", "phone", "location", "professional_summary", 
                      "career_goals", "unique_value_proposition", "linkedin_url", 
                      "github_url", "portfolio_url"]:
            value = data.get(field)
            if value and isinstance(value, str):
                cleaned[field] = value.strip()
            else:
                cleaned[field] = None
        
        # Normalize common aliases before array cleanup
        if not data.get("work_experience"):
            data["work_experience"] = (
                data.get("experience")
                or data.get("professional_experience")
                or data.get("employment_history")
                or []
            )

        # Arrays
        for field in ["education", "work_experience", "skills", "projects", "certifications", "awards"]:
            value = data.get(field, [])
            if isinstance(value, list):
                cleaned[field] = value
            else:
                cleaned[field] = []

        # Keep alias for downstream consumers that still read `experience`.
        cleaned["experience"] = cleaned["work_experience"]
        
        return cleaned


        return cleaned


# Singleton instance
_resume_parser: Optional[ResumeParser] = None


def get_resume_parser() -> ResumeParser:
    """Get or create resume parser instance."""
    global _resume_parser
    if _resume_parser is None:
        _resume_parser = ResumeParser()
    return _resume_parser
