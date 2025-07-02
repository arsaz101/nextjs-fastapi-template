from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from ..ai_service import ai_service
from ..file_service import file_service

router = APIRouter(prefix="/doc-updates", tags=["documentation"])


# Pydantic models for request/response
class DocUpdateQuery(BaseModel):
    query: str


class DocSuggestion(BaseModel):
    id: int
    section: str
    suggestion: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None


class DocUpdateRequest(BaseModel):
    suggestions: List[DocSuggestion]


class DocUpdateResponse(BaseModel):
    suggestions: List[DocSuggestion]
    message: str


class ApplyResponse(BaseModel):
    message: str
    success: List[dict]
    errors: List[dict]
    backups: List[str]


@router.post("/suggest", response_model=DocUpdateResponse)
async def get_doc_suggestions(query: DocUpdateQuery):
    """
    Get AI-generated suggestions for documentation updates based on user query.
    """
    try:
        # Use AI service to generate suggestions
        ai_suggestions = await ai_service.generate_doc_suggestions(query.query)

        # Convert to DocSuggestion objects
        suggestions = []
        for i, suggestion in enumerate(ai_suggestions, 1):
            suggestions.append(
                DocSuggestion(
                    id=suggestion.get("id", i),
                    section=suggestion.get("section", "General"),
                    suggestion=suggestion.get("suggestion", ""),
                    file_path=suggestion.get("file_path"),
                    line_number=suggestion.get("line_number"),
                )
            )

        return DocUpdateResponse(
            suggestions=suggestions, message="Suggestions generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating suggestions: {str(e)}"
        )


@router.post("/apply", response_model=ApplyResponse)
async def apply_doc_updates(updates: DocUpdateRequest):
    """
    Apply approved/edited documentation updates to files.
    """
    try:
        # Convert to dictionary format for file service
        suggestions_dict = []
        for suggestion in updates.suggestions:
            suggestions_dict.append(
                {
                    "id": suggestion.id,
                    "section": suggestion.section,
                    "suggestion": suggestion.suggestion,
                    "file_path": suggestion.file_path,
                    "line_number": suggestion.line_number,
                }
            )

        # Apply suggestions using file service
        results = file_service.apply_suggestions(suggestions_dict)

        return ApplyResponse(
            message=f"Applied {len(results['success'])} updates successfully",
            success=results["success"],
            errors=results["errors"],
            backups=results["backups"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying updates: {str(e)}")


@router.get("/files")
async def list_documentation_files():
    """
    List all documentation files available for updates.
    """
    try:
        files = file_service.get_documentation_files()
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@router.get("/backups")
async def list_backups():
    """
    List all backup files created during updates.
    """
    try:
        backups = file_service.list_backups()
        return {"backups": backups, "count": len(backups)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing backups: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for documentation updater service.
    """
    return {"status": "healthy", "service": "doc-updater"}
