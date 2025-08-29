# backend/services/enhanced_chat_service.py
import re
import logging
from typing import List, Optional, Dict, Any
from db.database import mongo_db
from services.llm_service import llm_service
from utils.helpers import convert_objectid_to_str

logger = logging.getLogger(__name__)

class EnhancedChatService:
    """Enhanced chat service with page-specific query support"""
    
    def extract_page_numbers_from_query(self, query: str) -> List[int]:
        """Extract page numbers from user query (e.g., 'page 5', 'pages 3-7', 'on page 10')"""
        page_numbers = []
        
        # Match patterns like "page 5", "pages 3-7", "on page 10"
        patterns = [
            r'\bpage\s+(\d+)\b',
            r'\bpages\s+(\d+)-(\d+)\b',
            r'\bpages\s+(\d+)\s+to\s+(\d+)\b',
            r'\bon\s+page\s+(\d+)\b',
            r'\bfrom\s+page\s+(\d+)\b',
            r'\bpage\s+number\s+(\d+)\b'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, query.lower())
            for match in matches:
                if len(match.groups()) == 1:
                    # Single page
                    page_numbers.append(int(match.group(1)))
                elif len(match.groups()) == 2:
                    # Page range
                    start, end = int(match.group(1)), int(match.group(2))
                    page_numbers.extend(range(start, min(end + 1, start + 10)))  # Limit range to 10 pages
        
        return list(set(page_numbers))  # Remove duplicates
    
    async def search_specific_pages(self, page_numbers: List[int], query_filter: Dict) -> List[Dict]:
        """Search for content in specific pages"""
        try:
            # Search in pages collection
            page_filter = {**query_filter, "page_number": {"$in": page_numbers}}
            pages = await mongo_db.db["pages"].find(page_filter).to_list(length=None)
            pages = convert_objectid_to_str(pages)
            
            # Also search sections that belong to these pages
            section_filter = {**query_filter, "page": {"$in": page_numbers}}
            sections = await mongo_db.db["sections"].find(section_filter).to_list(length=None)
            sections = convert_objectid_to_str(sections)
            
            # Combine and format results
            results = []
            
            # Add page content
            for page in pages:
                results.append({
                    "title": f"Page {page.get('page_number')} - Full Content",
                    "content": page.get("content", ""),
                    "source": page.get("source", "document"),
                    "page": page.get("page_number"),
                    "document_id": page.get("document_id"),
                    "type": "page"
                })
            
            # Add relevant sections from these pages
            for section in sections:
                results.append({
                    "title": section.get("title", "Untitled Section"),
                    "content": section.get("content", ""),
                    "source": section.get("source", "document"),
                    "page": section.get("page"),
                    "document_id": section.get("document_id"),
                    "type": "section"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching specific pages: {e}")
            return []
    
    async def search_all_content(self, query: str, query_filter: Dict) -> List[Dict]:
        """Search all content using keyword matching"""
        try:
            # Fetch sections from database
            all_sections = await mongo_db.db["sections"].find(query_filter).to_list(length=None)
            all_sections = convert_objectid_to_str(all_sections)
            
            # Simple keyword matching
            search_words = set(re.findall(r'\b\w+\b', query.lower()))
            matching_sections = []
            
            for section in all_sections:
                content = section.get("content", "").lower()
                title = section.get("title", "").lower()
                
                # Count matching words
                content_words = set(re.findall(r'\b\w+\b', content))
                title_words = set(re.findall(r'\b\w+\b', title))
                
                content_matches = len(search_words.intersection(content_words))
                title_matches = len(search_words.intersection(title_words))
                
                # Calculate simple relevance score
                total_matches = content_matches + (title_matches * 2)  # Weight title matches more
                if total_matches > 0:
                    relevance = total_matches / len(search_words)
                    matching_sections.append({
                        "section": section,
                        "relevance": relevance,
                        "matches": total_matches
                    })
            
            # Sort by relevance and take top 5
            matching_sections.sort(key=lambda x: x["relevance"], reverse=True)
            return [item["section"] for item in matching_sections[:5]]
            
        except Exception as e:
            logger.error(f"Error in content search: {e}")
            return []
    
    async def generate_response(self, query: str, context_sections: List[Dict]) -> str:
        """Generate LLM response based on context"""
        try:
            if not context_sections:
                return "I couldn't find any relevant information in your documents for that question. Try rephrasing or asking about different topics."
            
            # Create context for LLM
            context_text = "\n\n".join([
                f"From {section.get('source', 'document')} (Page {section.get('page', 'N/A')}):\n"
                f"{'Section: ' + section.get('title', 'Untitled') if section.get('type') != 'page' else 'Full Page Content'}:\n"
                f"Content: {section.get('content', '')[:800]}..."
                for section in context_sections[:3]  # Limit to top 3 for context length
            ])
            
            # Create conversational prompt
            conversational_prompt = f"""Based on the following content from the user's documents, please answer their question in a helpful and conversational way.

User Question: {query}

Relevant Content:
{context_text}

Please provide a helpful, direct answer based on this content. Keep it conversational and brief (2-3 sentences). If the user asked about specific pages, mention the page numbers in your response."""
            
            # Generate response using LLM
            if not llm_service.model:
                llm_service.configure()
            
            response = await llm_service.model.generate_content_async(conversational_prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "I found relevant information in your documents, but I'm having trouble generating a response right now. Please try again."
    
    async def chat_with_documents(self, query: str, cluster_id: str = None, document_ids: List[str] = None) -> Dict[str, Any]:
        """
        Enhanced chat function with page-specific query support
        """
        try:
            logger.info(f"Enhanced chat search for query: {query}")
            
            # Extract page numbers from query
            requested_pages = self.extract_page_numbers_from_query(query)
            logger.info(f"Extracted page numbers from query: {requested_pages}")
            
            # Build query filter
            query_filter = {}
            if cluster_id:
                query_filter["cluster_id"] = cluster_id
            if document_ids:
                query_filter["document_id"] = {"$in": document_ids}
            
            context_sections = []
            
            # If specific pages are requested, prioritize page content
            if requested_pages:
                logger.info(f"Searching specific pages: {requested_pages}")
                context_sections = await self.search_specific_pages(requested_pages, query_filter)
                
                if context_sections:
                    answer = await self.generate_response(query, context_sections)
                    return {
                        "answer": answer,
                        "relevant_sections": context_sections[:5],  # Limit returned sections
                        "success": True,
                        "page_specific": True,
                        "pages_found": requested_pages
                    }
            
            # Fallback to regular content search
            logger.info("Performing general content search")
            context_sections = await self.search_all_content(query, query_filter)
            
            if not context_sections:
                return {
                    "answer": "I don't have any documents to search through or couldn't find relevant information. Please upload some PDFs first or try rephrasing your question.",
                    "relevant_sections": [],
                    "success": True,
                    "page_specific": False
                }
            
            answer = await self.generate_response(query, context_sections)
            
            return {
                "answer": answer,
                "relevant_sections": context_sections,
                "success": True,
                "page_specific": False
            }
            
        except Exception as e:
            logger.error(f"Enhanced chat error: {e}")
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "relevant_sections": [],
                "success": False,
                "error": str(e)
            }

# Create global instance
enhanced_chat_service = EnhancedChatService()
