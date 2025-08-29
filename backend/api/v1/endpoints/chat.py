# backend/api/v1/endpoints/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.recommendation_engine import recommendation_service
from services.llm_service import llm_service
from services.enhanced_chat_service import enhanced_chat_service
from db.database import mongo_db
import logging
import re

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    cluster_id: Optional[str] = None
    document_ids: Optional[List[str]] = None

class ChatResponse(BaseModel):
    answer: str
    relevant_sections: List[dict]
    success: bool
    error: Optional[str] = None

async def simple_text_chat_search(request: ChatRequest, all_sections: List[dict]):
    """Fallback text-based search for chat when semantic search is not available"""
    try:
        query_words = set(re.findall(r'\b\w+\b', request.query.lower()))
        matching_sections = []

        for section in all_sections:
            content = section.get("content", "").lower()
            title = section.get("title", "").lower()

            # Count matching words
            content_words = set(re.findall(r'\b\w+\b', content))
            title_words = set(re.findall(r'\b\w+\b', title))

            content_matches = len(query_words.intersection(content_words))
            title_matches = len(query_words.intersection(title_words))

            # Calculate simple relevance score
            total_matches = content_matches + (title_matches * 2)
            if total_matches > 0:
                relevance = total_matches / len(query_words)
                matching_sections.append({
                    "section": section,
                    "relevance": relevance
                })

        # Sort by relevance and take top 3
        matching_sections.sort(key=lambda x: x["relevance"], reverse=True)
        top_sections = matching_sections[:3]

        if not top_sections:
            return ChatResponse(
                answer="I couldn't find relevant information in your documents to answer that question. Could you try rephrasing or asking about something more specific?",
                relevant_sections=[],
                success=True
            )

        # Create context from top sections
        context_parts = []
        context_sections = []

        for item in top_sections:
            section = item["section"]
            context_parts.append(f"From '{section.get('title', 'Untitled')}': {section.get('content', '')[:300]}...")
            context_sections.append({
                "title": section.get("title", "Untitled"),
                "content": section.get("content", "")[:200] + "...",
                "page": section.get("page", 1),
                "relevance": item["relevance"]
            })

        context_text = "\n\n".join(context_parts)

        # Create a simple prompt for the LLM
        conversational_prompt = f"""Based on the following content from the user's documents, provide a brief, conversational answer to their question.

User's question: "{request.query}"

Relevant content:
{context_text}

Please provide a helpful, direct answer based on this content. Keep it conversational and brief (2-3 sentences)."""

        # Generate response using LLM
        if not llm_service.model:
            llm_service.configure()

        try:
            response = await llm_service.model.generate_content_async(conversational_prompt)
            answer = response.text.strip()
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            answer = "I found some relevant information in your documents, but I'm having trouble generating a response right now. Please try again."

        return ChatResponse(
            answer=answer,
            relevant_sections=context_sections,
            success=True
        )

    except Exception as e:
        logger.error(f"Simple text chat search error: {e}")
        return ChatResponse(
            answer="I encountered an error while searching your documents. Please try again.",
            relevant_sections=[],
            success=False,
            error=str(e)
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """
    Chat endpoint for the "Talk to PDF" voice assistant.
    Performs RAG (Retrieval-Augmented Generation) using vector search and LLM.
    """
    try:
        if not request.query or len(request.query.strip()) < 3:
            raise HTTPException(status_code=400, detail="Query must be at least 3 characters long")

        logger.info(f"Enhanced chat request: {request.query}")

        # Use enhanced chat service
        result = await enhanced_chat_service.chat_with_documents(
            query=request.query,
            cluster_id=request.cluster_id,
            document_ids=request.document_ids
        )

        return ChatResponse(
            answer=result["answer"],
            relevant_sections=result["relevant_sections"],
            success=result["success"],
            error=result.get("error")
        )




    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(
            answer="I encountered an error while processing your question. Please try again.",
            relevant_sections=[],
            success=False,
            error=str(e)
        )
