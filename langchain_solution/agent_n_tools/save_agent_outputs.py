import os
import datetime
import logging
import json
from typing import List
from langchain_core.messages import BaseMessage, AIMessage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def save_agent_output(stage: str, result: dict, error_type: str = None) -> str:
    """
    Save agent output/error to a nicely formatted file.

    Args:
        stage: "extraction" or "solver"
        result: The result dict from agent.invoke() or error context
        error_type: Type of error (e.g., "RECURSION_LIMIT", "EXCEPTION")

    Returns:
        Path to saved file
    """
    output_dir = "agent_outputs"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_marker = f"_{error_type}" if error_type else ""
    filename = f"agent_output_{stage}{error_marker}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "stage": stage,
        "error_type": error_type,
        "messages": []
    }

    # Extract and format messages
    if isinstance(result, dict) and "messages" in result:
        for i, msg in enumerate(result["messages"], 1):
            msg_dict = {
                "index": i,
                "type": msg.__class__.__name__,
                "content": ""
            }

            # Handle different message types
            if hasattr(msg, 'content'):
                content = msg.content
                if isinstance(content, str):
                    msg_dict["content"] = content
                elif isinstance(content, list):
                    msg_dict["content"] = str(content)
                else:
                    msg_dict["content"] = str(content)
            elif isinstance(msg, dict):
                msg_dict["content"] = msg.get("content", str(msg))
            else:
                msg_dict["content"] = str(msg)

            # Add metadata if available
            if hasattr(msg, 'tool_calls'):
                msg_dict["tool_calls"] = [
                    {"tool_name": tc.name, "args": tc.args}
                    for tc in msg.tool_calls
                ] if msg.tool_calls else []

            output_data["messages"].append(msg_dict)

    # Save to file
    with open(filepath, "w") as f:
        json.dump(output_data, f, indent=2)

    logger.info(f"✓ Agent output saved to: {filepath}")
    return filepath

def saveToolMessages(self, messages: List[BaseMessage]) -> None:
        """
        Save tool call messages to a log file for debugging in tool_calls/ directory.

        Args:
            messages: List of BaseMessage objects containing tool calls
        """
        toolMessages = []
        try:
            # Extract tool calls from AIMessage objects
            for message in messages:
                if isinstance(message, AIMessage) and hasattr(message, 'tool_calls'):
                    if message.tool_calls:
                        for tool_call in message.tool_calls:
                            # Handle both dict and object formats
                            if isinstance(tool_call, dict):
                                toolMessages.append({
                                    "name": tool_call.get('name'),
                                    "args": tool_call.get('args'),
                                    "id": tool_call.get('id', None)
                                })
                            else:
                                toolMessages.append({
                                    "name": tool_call.name,
                                    "args": tool_call.args,
                                    "id": getattr(tool_call, 'id', None)
                                })

            if not toolMessages:
                return

            # Create tool_calls directory in same location as this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tool_calls_dir = os.path.join(script_dir, "tool_calls")
            os.makedirs(tool_calls_dir, exist_ok=True)

            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(tool_calls_dir, f"tool_calls_{timestamp}.json")

            with open(filepath, "w") as f:
                json.dump(toolMessages, f, indent=2)
            logger.info(f"[TOOLS] Saved {len(toolMessages)} tool calls to tool_calls/")
        except Exception as e:
            logger.error(f"[TOOLS] Error saving tool calls: {str(e)}", exc_info=True)
