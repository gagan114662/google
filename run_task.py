import argparse
import os
import shutil
from app.tools import file_system, content_generator, web_scraper
from app.skills import web_research, reporting
from app.skills.planning import skill_create_execution_plan
# from app.core.tool_manifest import get_tool_manifest # Not needed directly by orchestrator, but by planner skill
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TaskRunner")

WORKSPACE_DIR = "workspace"

def setup_workspace():
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR)
    logger.info(f"Workspace directory '{WORKSPACE_DIR}' created/cleaned.")

class TaskOrchestrator:
    def __init__(self):
        self.results_history = {}
        self.callable_tool_map = self._get_callable_tool_map()

    def _get_callable_tool_map(self):
        # This map needs to be kept in sync with tool_manifest.py and actual function locations
        # For dynamic loading, one might inspect modules, but a map is simpler for now.
        # Ensure all imported tools and skills are correctly referenced here.
        return {
            "app.tools.web_scraper.fetch_html": web_scraper.fetch_html,
            "app.tools.web_scraper.parse_html_to_text": web_scraper.parse_html_to_text,
            "app.tools.web_scraper.fetch_html_dynamic": web_scraper.fetch_html_dynamic,
            "app.tools.web_scraper.capture_screenshot_dynamic": web_scraper.capture_screenshot_dynamic,
            "app.tools.web_scraper.search_google_dynamic": web_scraper.search_google_dynamic,
            "app.tools.web_scraper.search_google": web_scraper.search_google,
            "app.tools.file_system.read_file": file_system.read_file,
            "app.tools.file_system.write_file": file_system.write_file,
            "app.tools.file_system.list_files": file_system.list_files,
            "app.tools.content_generator.generate_text_report": content_generator.generate_text_report,
            "app.tools.content_generator.generate_pdf_report_simple": content_generator.generate_pdf_report_simple,
            "app.tools.content_generator.create_excel_spreadsheet": content_generator.create_excel_spreadsheet,
            "app.tools.content_generator.generate_summary_local_llm": content_generator.generate_summary_local_llm,
            "app.tools.content_generator.generate_email_draft_local_llm": content_generator.generate_email_draft_local_llm,
            "app.skills.web_research.skill_extract_text_from_url": web_research.skill_extract_text_from_url,
            "app.skills.web_research.skill_perform_basic_search": web_research.skill_perform_basic_search,
            "app.skills.web_research.skill_perform_dynamic_search": web_research.skill_perform_dynamic_search,
            "app.skills.reporting.skill_create_simple_text_report": reporting.skill_create_simple_text_report,
            "app.skills.reporting.skill_create_simple_pdf_report": reporting.skill_create_simple_pdf_report,
            "app.skills.planning.skill_create_execution_plan": skill_create_execution_plan,
        }

    def execute_step(self, step_name: str, function_to_call, **kwargs):
        logger.info(f"[Orchestrator] Executing step: {step_name}")
        try:
            # Special handling for print during example tasks, not a real "tool"
            if function_to_call == print and ("example_step" in step_name or "conditional_step_example" in step_name) :
                 function_to_call(f"  Params for {step_name}: {kwargs.get('message')}")
                 result = f"Printed message for {step_name}"
            elif function_to_call is None: # Should ideally not happen with planner
                logger.debug(f"  Params: {kwargs}")
                result = f"No function provided for {step_name}, params: {kwargs}"
            else:
                logger.debug(f"  Calling function: {function_to_call.__name__} with params: {kwargs}")
                result = function_to_call(**kwargs)

            structured_result = {"status": "success", "data": result, "error_message": None}
            logger.info(f"[Orchestrator] Step '{step_name}' completed. Status: {structured_result['status']}, Data: {str(result)[:100]}...")
            self.results_history[step_name] = structured_result
            return structured_result
        except Exception as e:
            error_msg = f"Error in step '{step_name}' calling {function_to_call.__name__ if function_to_call else 'None'} : {e}"
            logger.error(f"[Orchestrator] {error_msg}")
            # import traceback; traceback.print_exc() # Uncomment for detailed debug
            structured_result = {"status": "failure", "data": None, "error_message": str(e)}
            self.results_history[step_name] = structured_result
            return structured_result

    def execute_loop(self, loop_name: str, items: list, function_to_call, static_kwargs: dict = None, item_kwarg_name: str = "item"):
        logger.info(f"[Orchestrator] Starting loop: {loop_name} for {len(items)} items.")
        loop_results = []
        if static_kwargs is None: static_kwargs = {}
        for index, item_val in enumerate(items):
            step_name = f"{loop_name}_item_{index+1}"
            current_kwargs = {**static_kwargs, item_kwarg_name: item_val}
            result = self.execute_step(step_name, function_to_call, **current_kwargs)
            loop_results.append(result)
            if result["status"] == "failure":
                 logger.warning(f"[Orchestrator] Loop '{loop_name}' item {index+1} failed. Continuing...")
        logger.info(f"[Orchestrator] Loop '{loop_name}' completed.")
        self.results_history[loop_name] = loop_results
        return loop_results

    def _print_history_summary(self):
        logger.info("\n--- Task Execution History Summary ---")
        for step, res_hist_item in self.results_history.items():
            if isinstance(res_hist_item, list) and ("loop" in step.lower()):
                 logger.info(f"  Loop Summary '{step}': Processed {len(res_hist_item)} items (details logged during execution).")
            elif isinstance(res_hist_item, dict):
                 logger.info(f"  Step '{step}': Status: {res_hist_item.get('status')}, Data (preview): {str(res_hist_item.get('data'))[:70]}..., Error: {res_hist_item.get('error_message')}")
            else:
                 logger.info(f"  Step '{step}': Unexpected result type in history: {type(res_hist_item)}")

    # --- Existing Task Methods ---
    def run_example_task(self):
        logger.info("\n--- Starting Example Task ---")
        step1_result = self.execute_step("example_step_1", print, message="Executing example_step_1")
        if step1_result["status"] == "failure":
            logger.error(f"Task failed at step 1. Error: {step1_result['error_message']}. Aborting.")
            return
        if step1_result["status"] == "success":
            logger.info("[Orchestrator] Condition met: Step 1 successful. Proceeding.")
            self.execute_step("conditional_step_example",print,message=f"Conditional step using: {step1_result['data']}")
        else:
            logger.info("[Orchestrator] Condition NOT met: Step 1 failed. Skipping conditional_step.")
        sample_items = ["apple", "banana", "cherry"]
        def process_item_func(item, prefix_message: str):
            msg = f"{prefix_message} Processing item: {item}"
            logger.debug(f"    [Loop Item] {msg}")
            return msg
        self.execute_loop("example_item_processing_loop", sample_items, process_item_func, {"prefix_message": "Fruit:"}, "item")
        logger.info("\n--- Example Task Completed ---")
        self._print_history_summary()

    def run_excel_lotto_task(self):
        logger.info("\n--- Starting Excel Lotto Task ---")
        lotto_data = {"headers": ["Game Name", "Description", "Draw Frequency"], "rows": [["Lotto", "Classic", "3/week"], ["10eLotto", "5min draw", "Every 5 min"]]}
        excel_filename = "italian_lottery_games.xlsx"
        s1 = self.execute_step("generate_lottery_excel",content_generator.create_excel_spreadsheet,filename=excel_filename,data=lotto_data["rows"],headers=lotto_data["headers"])
        if s1["status"] == "failure" or not s1["data"]: logger.error(f"Excel generation failed: {s1.get('error_message')}"); return
        s2 = self.execute_step("list_files",file_system.list_files,dirpath=".")
        if s2["status"] == "success" and excel_filename in s2["data"]: logger.info(f"SUCCESS: '{excel_filename}' found.")
        else: logger.error(f"ERROR: '{excel_filename}' NOT found. Listing: {s2.get('data')}")
        logger.info("\n--- Excel Lotto Task Completed ---")
        self._print_history_summary()

    def run_dynamic_scrape_test_task(self):
        logger.info("\n--- Starting Dynamic Scrape Test Task ---")
        logger.warning("IMPORTANT: This task uses Botasaurus (needs Xvfb).")
        js_url = "http://quotes.toscrape.com/js/"
        txt_file = "dynamic_quotes.txt"; ss_file = "dynamic_scrape.png"
        s1 = self.execute_step("extract_text_dynamic",web_research.skill_extract_text_from_url,url=js_url,use_dynamic_fetch=True)
        extracted = s1["data"] if s1["status"] == "success" and isinstance(s1["data"], str) else None
        if extracted: self.execute_step("save_extracted",file_system.write_file,filepath=txt_file,content=extracted)
        self.execute_step("dynamic_search",web_research.skill_perform_dynamic_search,query="famous quotes",num_results=1)
        self.execute_step("screenshot",web_scraper.capture_screenshot_dynamic,url=js_url,output_filename=ss_file)
        logger.info("\n--- Dynamic Scrape Test Task Completed ---")
        self._print_history_summary()

    def run_local_llm_test_summary_task(self):
        logger.info("\n--- Starting Local LLM Test Summary Task ---")
        logger.warning(f"IMPORTANT: Uses Ollama. Model: '{content_generator.get_default_model_name()}'")
        text = "AlphaCentauri X1 rocket by StarLeap Inc. had a successful 120km suborbital test. Aims for commercial space tourism by 2027 with a reusable hybrid engine."
        s1 = self.execute_step("summarize_text_llm",content_generator.generate_summary_local_llm,text_to_summarize=text,max_length=50)
        if s1["status"] == "success" and s1["data"]: logger.info(f"Original: {text}\nSummary: {s1['data']}")
        logger.info("\n--- Local LLM Test Summary Task Completed ---")
        self._print_history_summary()

    def run_scrape_forum_discussions_task(self, search_query: str, num_forums_to_scrape: int = 1, max_chars_page: int = 1500, total_max_chars:int = 3000): # Reduced for faster test
        logger.info(f"\n--- Starting Scrape Forum Discussions for: '{search_query}' ---")
        logger.warning("IMPORTANT: Uses Botasaurus (Xvfb) and Ollama.")
        s_search = self.execute_step("find_forum_links",web_research.skill_perform_dynamic_search,query=f"{search_query} forum discussion",num_results=num_forums_to_scrape)
        if s_search["status"] == "failure" or not s_search["data"]: logger.error(f"Search failed: {s_search['error_message']}"); return
        links = [item["link"] for item in s_search["data"][:num_forums_to_scrape]]
        if not links: logger.info("No links to scrape."); return
        scraped_results = self.execute_loop("scrape_forum_pages",links,web_research.skill_extract_text_from_url,static_kwargs={"use_dynamic_fetch": True},item_kwarg_name="url")
        all_text = [res["data"][:max_chars_page] for res in scraped_results if res["status"] == "success" and res["data"]]
        summary = "No summary (no content or LLM issue)."
        if all_text:
            combined = "\n\n---\n\n".join(all_text)[:total_max_chars]
            sys_prompt = "Summarize key topics, opinions from these forum excerpts."
            s_sum = self.execute_step("summarize_forums",content_generator.generate_summary_local_llm,text_to_summarize=combined,max_length=200, custom_system_prompt=sys_prompt)
            if s_sum["status"] == "success" and s_sum["data"]: summary = s_sum["data"]
            if not content_generator.OLLAMA_IS_AVAILABLE() and s_sum["status"] == "success": summary += " (Placeholder)"
        logger.info(f"Summary:\n{summary}")
        report = f"Query: {search_query}\nLinks: {s_search['data']}\nSummary: {summary}"
        self.execute_step("save_forum_report",file_system.write_file,filepath=f"forum_report_{search_query[:10]}.txt",content=report)
        logger.info("\n--- Scrape Forum Discussions Task Completed ---")
        self._print_history_summary()

    # --- New Task Method for Auto-Generated Plans ---
    def run_auto_generated_plan_task(self, user_goal: str):
        logger.info(f"\n--- Starting Auto-Generated Plan Task for Goal: '{user_goal}' ---")
        logger.warning("IMPORTANT: This task uses Ollama for planning and may use Botasaurus (Xvfb) for execution.")

        plan_generation_result = self.execute_step(
            step_name="generate_execution_plan",
            function_to_call=skill_create_execution_plan,
            user_goal=user_goal
        )

        if plan_generation_result["status"] == "failure" or not plan_generation_result["data"]:
            logger.error(f"Failed to generate execution plan. Error: {plan_generation_result['error_message']}. Aborting.")
            return

        plan = plan_generation_result["data"]
        if not isinstance(plan, list) or not plan:
            logger.error(f"Planning skill returned an empty or invalid plan: {plan}. Aborting.")
            self.results_history["execute_planned_steps"] = {"status":"failure", "data": None, "error_message": "Empty or invalid plan from LLM."}
            return

        logger.info(f"Successfully generated plan with {len(plan)} steps:")
        for i, step_def in enumerate(plan):
            logger.info(f"  Plan Step {i+1}: Tool/Skill: {step_def.get('tool_or_skill_name')}, Params: {step_def.get('parameters')}")

        logger.info("\n--- Executing Generated Plan ---")
        step_outputs_context = {} # To store outputs of steps for potential context passing

        for i, step_def in enumerate(plan):
            tool_name = step_def.get("tool_or_skill_name")
            params = step_def.get("parameters", {})

            if not tool_name or not isinstance(params, dict):
                logger.error(f"  Plan Step {i+1}: Invalid step definition: {step_def}. Skipping.")
                self.results_history[f"auto_plan_step_{i+1}_invalid"] = {"status": "failure", "data": None, "error_message": "Invalid step definition from LLM."}
                continue

            # Basic context injection from previous steps' outputs
            processed_params = {}
            for p_name, p_value in params.items():
                if isinstance(p_value, str) and p_value.startswith("{") and p_value.endswith("_output}"):
                    ref_step_key = p_value[1:-1] # e.g., "{step_1_data_output}" -> "step_1_data"
                    # We need a convention for how planner refers to outputs.
                    # Let's assume LLM plan refers to "step_N_output" which maps to the "data" field of that step's result.
                    ref_step_index_str = ref_step_key.split("_")[1] # "1" from "step_1_output"
                    # The actual key in results_history for a successfully executed plan step is like "auto_plan_step_1_..."
                    # This context passing is tricky if step names aren't known beforehand by the LLM.
                    # For now, let's assume simple numbered step outputs.
                    # The LLM should be prompted to refer to output of "step N" as e.g. "{{step_N_data}}"

                    # Simplified: if param value is "{step_X_data}", try to get data from history for "auto_plan_step_X_..."
                    if p_value.startswith("{step_") and p_value.endswith("_data}"):
                        try:
                            idx = int(ref_step_index_str)
                            # Find the actual history key for that step. This is fragile.
                            # A better way would be for the LLM to name its output variables and refer to them.
                            # For now, this is a placeholder for a more robust context system.
                            # Let's assume the LLM just passes the direct value it thinks is right for now, or simple placeholder.
                            # This placeholder replacement is too naive for robust use.
                            # The LLM should be taught to construct parameters based on the goal.
                            # For now, we'll just use the params as given by the LLM, assuming it's smart.
                            pass # Not implementing placeholder replacement yet.
                        except ValueError:
                            pass # Not a valid step reference
                processed_params[p_name] = p_value


            if tool_name not in self.callable_tool_map:
                logger.error(f"  Plan Step {i+1}: Tool/Skill '{tool_name}' not found in callable map. Skipping.")
                self.results_history[f"auto_plan_step_{i+1}_{tool_name.split('.')[-1]}"] = {"status": "failure", "data": None, "error_message": f"Tool '{tool_name}' not found."}
                continue

            executable_function = self.callable_tool_map[tool_name]
            logger.info(f"Executing Plan Step {i+1}: {tool_name} with params: {processed_params}")

            step_result = self.execute_step(
                step_name=f"auto_plan_step_{i+1}_{tool_name.split('.')[-1]}",
                function_to_call=executable_function,
                **processed_params
            )

            if step_result["status"] == "failure":
                logger.error(f"  Plan Step {i+1} ('{tool_name}') failed. Error: {step_result['error_message']}. Halting plan execution.")
                break

        logger.info("\n--- Auto-Generated Plan Execution Completed ---")
        self._print_history_summary()

def main():
    parser = argparse.ArgumentParser(description="Chimera Local Task Runner")
    parser.add_argument("task_name", type=str, help="Name of the task (e.g., 'example', 'auto_goal').")
    parser.add_argument("--query", type=str, default=None, help="Search query for 'scrape_forums'.")
    parser.add_argument("--goal", type=str, default=None, help="User goal for 'auto_goal' task.")
    args = parser.parse_args()

    setup_workspace()
    orchestrator = TaskOrchestrator()

    if args.task_name == "example": orchestrator.run_example_task()
    elif args.task_name == "excel_lotto": orchestrator.run_excel_lotto_task()
    elif args.task_name == "dynamic_scrape_test": orchestrator.run_dynamic_scrape_test_task()
    elif args.task_name == "local_llm_test_summary": orchestrator.run_local_llm_test_summary_task()
    elif args.task_name == "scrape_forums":
        if not args.query: logger.error("Task 'scrape_forums' requires --query."); return
        orchestrator.run_scrape_forum_discussions_task(search_query=args.query)
    elif args.task_name == "auto_goal":
        if not args.goal: logger.error("Task 'auto_goal' requires --goal."); return
        orchestrator.run_auto_generated_plan_task(user_goal=args.goal)
    else:
        logger.error(f"Unknown task: {args.task_name}")
        print(f"Available tasks: example, excel_lotto, dynamic_scrape_test, local_llm_test_summary, scrape_forums, auto_goal")

if __name__ == "__main__":
    main()
