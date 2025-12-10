from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sources.schemas import QueryRequest, QueryResponse
from sources.logger import Logger
from sources.utility import pretty_print
import uuid
import sys
import asyncio

router = APIRouter()
logger = Logger("query_router.log")

# Placeholder for the interaction service
interaction_service = None 
is_generating = False
query_resp_history = []

def set_interaction_service(service):
    global interaction_service
    interaction_service = service

async def think_wrapper(interaction, query):
    try:
        interaction.last_query = query
        logger.info("Agents request is being processed")
        success = await interaction.think()
        if not success:
            interaction.last_answer = "Error: No answer from agent"
            interaction.last_reasoning = "Error: No reasoning from agent"
            interaction.last_success = False
        else:
            interaction.last_success = True
        pretty_print(interaction.last_answer)
        interaction.speak_answer()
        return success
    except Exception as e:
        logger.error(f"Error in think_wrapper: {str(e)}")
        interaction.last_answer = f""
        interaction.last_reasoning = f"Error: {str(e)}"
        interaction.last_success = False
        raise e

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    global is_generating, query_resp_history
    
    if interaction_service is None:
        return JSONResponse(status_code=500, content={"error": "Interaction service not initialized"})
    
    interaction = interaction_service.get_interaction()
    
    logger.info(f"Processing query: {request.query}")
    query_resp = QueryResponse(
        done="false",
        answer="",
        reasoning="",
        agent_name="Unknown",
        success="false",
        blocks={},
        status="Ready",
        uid=str(uuid.uuid4())
    )
    if is_generating:
        logger.warning("Another query is being processed, please wait.")
        return JSONResponse(status_code=429, content=query_resp.jsonify())

    try:
        is_generating = True
        
        # Update provider if specified
        if request.provider and request.model:
            logger.info(f"Switching provider to {request.provider} with model {request.model}")
            # Assuming interaction.agents[0].provider is the shared provider instance
            # Or access via interaction_service.provider if accessible
            # Since we don't have direct access to interaction_service.provider here easily without getter
            # We can access it via the first agent in interaction
            if interaction.agents:
                provider_instance = interaction.agents[0].provider
                provider_instance.provider_name = request.provider
                provider_instance.model = request.model
                # Also update the available_providers dict if needed? 
                # No, available_providers is a dict of functions, provider_name selects the key.
                # We might need to re-initialize api_key if switching to a cloud provider that wasn't set?
                # The Provider class handles api_key fetching in __init__ but we might need to trigger it if switching.
                # Let's check Provider class again.
                if request.provider in provider_instance.unsafe_providers:
                     # Re-fetch API key just in case it wasn't loaded (though get_api_key loads dotenv)
                     provider_instance.api_key = provider_instance.get_api_key(request.provider)

        success = await think_wrapper(interaction, request.query)
        is_generating = False

        if not success:
            query_resp.answer = interaction.last_answer
            query_resp.reasoning = interaction.last_reasoning
            return JSONResponse(status_code=400, content=query_resp.jsonify())

        if interaction.current_agent:
            blocks_json = {f'{i}': block.jsonify() for i, block in enumerate(interaction.current_agent.get_blocks_result())}
        else:
            logger.error("No current agent found")
            blocks_json = {}
            query_resp.answer = "Error: No current agent"
            return JSONResponse(status_code=400, content=query_resp.jsonify())

        logger.info(f"Answer: {interaction.last_answer}")
        logger.info(f"Blocks: {blocks_json}")
        query_resp.done = "true"
        query_resp.answer = interaction.last_answer
        query_resp.reasoning = interaction.last_reasoning
        query_resp.agent_name = interaction.current_agent.agent_name
        query_resp.success = str(interaction.last_success)
        query_resp.blocks = blocks_json
        
        query_resp_dict = {
            "done": query_resp.done,
            "answer": query_resp.answer,
            "agent_name": query_resp.agent_name,
            "success": query_resp.success,
            "blocks": query_resp.blocks,
            "status": query_resp.status,
            "uid": query_resp.uid
        }
        query_resp_history.append(query_resp_dict)

        logger.info("Query processed successfully")
        return JSONResponse(status_code=200, content=query_resp.jsonify())
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        # Don't exit the process, just return error
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        logger.info("Processing finished")
        # Access config via interaction service or global config if needed
        # For now, assuming save_session is handled within interaction or we need to pass config
        if interaction.recover_last_session: # Using attribute from interaction if available
             interaction.save_session()
