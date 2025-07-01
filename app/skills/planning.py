import json
import logging
from app.llm import ollama_client, OLLAMA_IS_AVAILABLE, get_default_model_name
from app.core.tool_manifest import get_tool_manifest

logger = logging.getLogger(__name__)

def _format_tools_for_prompt(manifest: list[dict]) -> str:
    """Formats the tool manifest into a string suitable for an LLM prompt."""
    formatted_tools = []
    for tool in manifest:
        params_str_parts = []
        for p in tool.get("parameters", []):
            param_desc = f"'{p['name']}' ({p['type']})"
            if not p.get('required', False):
                param_desc += f" (optional, default: {p.get('default', 'None')})"
            else:
                param_desc += " (required)"
            param_desc += f": {p['description']}"
            params_str_parts.append(f"    - {param_desc}")

        params_str = "\n".join(params_str_parts) if params_str_parts else "    (No parameters)"

        returns_info = tool.get("returns", {"type": "unknown", "description": "Not specified"})
        returns_str = f"  Returns: {returns_info['type']} - {returns_info['description']}"

        formatted_tools.append(
            f"- Name: {tool['name']}\n"
            f"  Description: {tool['description']}\n"
            f"  Parameters:\n{params_str}\n"
            f"{returns_str}"
        )
    return "\n\n".join(formatted_tools)

def skill_create_execution_plan(user_goal: str) -> list[dict] | None:
    """
    Uses a local LLM to create an execution plan (list of tool/skill calls)
    based on a user goal and the available tool manifest.

    Args:
        user_goal: The high-level goal described by the user.

    Returns:
        A list of dictionaries, where each dict represents a step with
        "tool_or_skill_name" and "parameters" (another dict).
        Returns None if planning fails or Ollama is unavailable.
    """
    logger.info(f"Attempting to create execution plan for goal: '{user_goal}'")

    if not OLLAMA_IS_AVAILABLE():
        logger.error("Ollama service is not available. Cannot create execution plan.")
        return None

    tool_manifest = get_tool_manifest()
    if not tool_manifest:
        logger.error("Tool manifest is empty. Cannot create execution plan.")
        return None

    formatted_tools = _format_tools_for_prompt(tool_manifest)

    system_prompt = (
        "You are an expert planning assistant. Your task is to take a user's goal "
        "and a list of available tools/skills, and break down the goal into a sequence of "
        "executable steps. Each step must be a call to one of the provided tools/skills."
        "\n\nConsider the user's goal carefully. For each step in your plan:"
        "\n1. Choose the most appropriate tool/skill from the list."
        "\n2. Determine all necessary parameters for that tool/skill based on the user's goal and the context of previous steps (if any)."
        "\n3. Ensure all *required* parameters for a tool/skill are provided."
        "\n4. If a parameter is optional and not explicitly needed for the goal, you can omit it or use its default if sensible."
        "\n5. Think step-by-step. The output of one step might be implicitly used as input or context for the next."
        "\n\nIMPORTANT: You MUST output your plan as a valid JSON list of dictionaries. "
        "Each dictionary in the list represents one step and must have exactly two keys:"
        "\n  - 'tool_or_skill_name': A string with the exact name of the tool/skill from the manifest (e.g., 'app.tools.file_system.read_file')."
        "\n  - 'parameters': A dictionary where keys are parameter names (strings) and values are the corresponding arguments for the tool/skill (strings, numbers, booleans, or lists where appropriate based on type; ensure numbers are not quoted if they should be numeric)."
        "\n\nExample of a single step in the JSON output:"
        '\n{\n  "tool_or_skill_name": "app.tools.web_scraper.search_google_dynamic",\n  "parameters": {\n    "query": "relevant search term",\n    "num_results": 3\n  }\n}'
        "\nDo NOT add any explanations or conversational text outside of the JSON list structure."
        "\nIf the goal is simple and requires only one tool call, the list will contain one dictionary."
        "\nIf the goal cannot be achieved with the available tools, output an empty JSON list: []."
    )

    user_prompt_for_planner = (
        f"User Goal: \"{user_goal}\"\n\n"
        f"Available Tools/Skills:\n"
        f"-------------------------\n"
        f"{formatted_tools}\n"
        f"-------------------------\n\n"
        f"Based on the user goal and the available tools/skills, provide an execution plan as a JSON list of dictionaries:"
    )

    model_to_use = get_default_model_name()
    # For planning, a more capable model is generally better.
    # If DEFAULT_OLLAMA_MODEL is set to a small one like orca-mini, planning quality might be low.
    # Consider allowing a specific planner_model_name or defaulting to a known capable one if available.
    # For now, uses the global default.

    logger.info(f"Requesting plan from Ollama model: {model_to_use}")
    # logger.debug(f"Full prompt for planner:\nSystem: {system_prompt}\nUser: {user_prompt_for_planner}") # Very verbose

    raw_llm_response = ollama_client.generate_text(
        prompt=user_prompt_for_planner,
        model_name=model_to_use,
        system_prompt=system_prompt,
        temperature=0.1 # Low temperature for more deterministic planning
    )

    if not raw_llm_response:
        logger.error("LLM did not return a response for planning.")
        return None

    logger.debug(f"Raw LLM response for plan:\n{raw_llm_response}")

    try:
        # The LLM might sometimes wrap the JSON in backticks or add explanations.
        # Try to extract the JSON part.
        json_start_index = raw_llm_response.find('[')
        json_end_index = raw_llm_response.rfind(']')

        if json_start_index != -1 and json_end_index != -1 and json_end_index > json_start_index:
            json_str = raw_llm_response[json_start_index : json_end_index+1]
            plan = json.loads(json_str)
            if isinstance(plan, list):
                # Basic validation of plan structure
                for step in plan:
                    if not isinstance(step, dict) or \
                       "tool_or_skill_name" not in step or \
                       "parameters" not in step or \
                       not isinstance(step["parameters"], dict):
                        logger.error(f"Invalid step structure in LLM plan: {step}")
                        raise ValueError("Invalid plan structure from LLM.")
                logger.info(f"Successfully parsed execution plan with {len(plan)} steps.")
                return plan
            else:
                logger.error(f"LLM response for plan was not a JSON list. Response: {raw_llm_response}")
                return None
        else:
            logger.error(f"Could not find valid JSON list in LLM response. Response: {raw_llm_response}")
            return None

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON plan from LLM response: {e}. Response was:\n{raw_llm_response}")
        return None
    except ValueError as e: # For our custom validation error
        logger.error(f"Plan validation failed: {e}")
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Testing Planner Skill ---")

    if not OLLAMA_IS_AVAILABLE():
        logger.warning("Ollama is not available. Live planner test will likely fail or be skipped by the skill.")

    # Test case 1: Simple goal
    goal1 = "Find out what the main page of example.com says and save it to a file called example_content.txt"
    logger.info(f"\nTesting with goal: \"{goal1}\"")
    plan1 = skill_create_execution_plan(goal1)
    if plan1:
        logger.info("Generated Plan 1:")
        for i, step in enumerate(plan1):
            logger.info(f"  Step {i+1}: {step['tool_or_skill_name']} with params {step['parameters']}")
    else:
        logger.info("Failed to generate Plan 1.")

    # Test case 2: Slightly more complex goal
    goal2 = "Search for 'best local coffee shops' and then write a short text report about the first two results."
    logger.info(f"\nTesting with goal: \"{goal2}\"")
    plan2 = skill_create_execution_plan(goal2)
    if plan2:
        logger.info("Generated Plan 2:")
        for i, step in enumerate(plan2):
            logger.info(f"  Step {i+1}: {step['tool_or_skill_name']} with params {step['parameters']}")
    else:
        logger.info("Failed to generate Plan 2.")

    # Test case 3: Goal that might be impossible with current tools
    goal3 = "Order a pizza for me."
    logger.info(f"\nTesting with goal: \"{goal3}\"")
    plan3 = skill_create_execution_plan(goal3)
    if plan3 is not None: # Could be an empty list if LLM deems it impossible
        logger.info(f"Generated Plan 3 (expected empty or few steps): {plan3}")
        if not plan3:
            logger.info("Correctly generated an empty plan for an impossible goal.")
    else:
        logger.info("Failed to generate Plan 3 (or LLM error).")

    logger.info("\n--- Planner Skill Test Complete ---")
    logger.info(f"Note: Plan quality depends heavily on the LLM ({get_default_model_name()}) and prompt engineering.")
