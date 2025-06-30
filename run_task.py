import argparse
import os
import shutil
from app.tools import file_system, content_generator, web_scraper
from app.skills import web_research
import logging # Added for cleaner logging

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TaskRunner")


# Define the workspace directory
WORKSPACE_DIR = "workspace"

def setup_workspace():
    """Creates or cleans the workspace directory."""
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR)
    logger.info(f"Workspace directory '{WORKSPACE_DIR}' created/cleaned.")

class TaskOrchestrator:
    def __init__(self):
        self.results_history = {}

    def execute_step(self, step_name: str, function_to_call, **kwargs):
        logger.info(f"[Orchestrator] Executing step: {step_name}")
        try:
            if function_to_call is None:
                logger.debug(f"  Params: {kwargs}")
                result = f"No function provided for {step_name}, params: {kwargs}"
            elif step_name in ["example_step_1", "example_step_2", "conditional_step_example"] and function_to_call == print:
                 function_to_call(f"  Params for {step_name}: {kwargs.get('message')}")
                 result = f"Printed message for {step_name}"
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
            # import traceback # Uncomment for debug
            # traceback.print_exc() # Uncomment for debug
            structured_result = {"status": "failure", "data": None, "error_message": str(e)}
            self.results_history[step_name] = structured_result
            return structured_result

    def execute_loop(self, loop_name: str, items: list, function_to_call, static_kwargs: dict = None, item_kwarg_name: str = "item"):
        logger.info(f"[Orchestrator] Starting loop: {loop_name} for {len(items)} items.")
        loop_results = []
        if static_kwargs is None:
            static_kwargs = {}

        for index, item_val in enumerate(items): # Renamed item to item_val to avoid conflict
            step_name = f"{loop_name}_item_{index+1}"
            current_kwargs = static_kwargs.copy()
            current_kwargs[item_kwarg_name] = item_val

            result = self.execute_step(step_name, function_to_call, **current_kwargs)
            loop_results.append(result)
            if result["status"] == "failure":
                 logger.warning(f"[Orchestrator] Loop '{loop_name}' item {index+1} failed. Continuing with next items unless logic prevents.")

        logger.info(f"[Orchestrator] Loop '{loop_name}' completed.")
        self.results_history[loop_name] = loop_results
        return loop_results

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
        def process_item_func(item, prefix_message: str): # item_kwarg_name will be 'item'
            msg = f"{prefix_message} Processing item: {item}"
            logger.debug(f"    [Loop Item] {msg}")
            return msg
        self.execute_loop("example_item_processing_loop", sample_items, process_item_func, {"prefix_message": "Fruit:"}, "item")
        logger.info("\n--- Example Task Completed ---")
        self._print_history_summary()

    def run_excel_lotto_task(self):
        logger.info("\n--- Starting Excel Lotto Task ---")
        lotto_data = {
            "headers": ["Game Name", "Description", "Draw Frequency", "Main Prize (Example)"],
            "rows": [
                ["Lotto", "Classic Italian number game", "3 times a week (Tue, Thu, Sat)", "€1,000,000+"],
                ["10eLotto", "Draws every 5 minutes, choose 10 numbers", "Every 5 minutes", "Up to €5,000,000"],
                ["MillionDAY", "Daily draw, pick 5 numbers to win €1,000,000", "Daily", "€1,000,000 (fixed)"]
            ]}
        excel_filename = "italian_lottery_games.xlsx"
        step1_res = self.execute_step("generate_lottery_excel",content_generator.create_excel_spreadsheet,filename=excel_filename,data=lotto_data["rows"],headers=lotto_data["headers"])
        if step1_res["status"] == "failure" or not step1_res["data"]:
            logger.error(f"Task failed at Excel generation. Error: {step1_res.get('error_message', 'Create_excel_spreadsheet returned False/None')}")
            return
        step2_res = self.execute_step("list_workspace_files",file_system.list_files,dirpath=".")
        if step2_res["status"] == "success" and excel_filename in step2_res["data"]:
            logger.info(f"SUCCESS: '{excel_filename}' found in workspace.")
        else:
            logger.error(f"ERROR: '{excel_filename}' NOT found in workspace. Listing: {step2_res.get('data')}, Error: {step2_res.get('error_message')}")
        logger.info("\n--- Excel Lotto Task Completed ---")
        self._print_history_summary()

    def run_dynamic_scrape_test_task(self):
        logger.info("\n--- Starting Dynamic Scrape Test Task ---")
        logger.warning("IMPORTANT: This task uses Botasaurus and likely needs 'xvfb-run'")
        js_reliant_url = "http://quotes.toscrape.com/js/"
        output_text_file = "dynamic_scraped_quotes.txt"
        screenshot_file = "dynamic_scrape_screenshot.png"

        s1 = self.execute_step("extract_text_dynamically",web_research.skill_extract_text_from_url,url=js_reliant_url,use_dynamic_fetch=True)
        extracted_text = s1["data"] if s1["status"] == "success" and isinstance(s1["data"], str) else None
        if extracted_text:
            self.execute_step("save_extracted_text",file_system.write_file,filepath=output_text_file,content=extracted_text)
        self.execute_step("perform_dynamic_search",web_research.skill_perform_dynamic_search,query="inspiration",num_results=1)
        self.execute_step("capture_screenshot",web_scraper.capture_screenshot_dynamic,url=js_reliant_url,output_filename=screenshot_file)
        logger.info("\n--- Dynamic Scrape Test Task Completed ---")
        self._print_history_summary()

    def run_local_llm_test_summary_task(self):
        logger.info("\n--- Starting Local LLM Test Summary Task ---")
        logger.warning(f"IMPORTANT: Uses Ollama. Model: '{content_generator.get_default_model_name()}'")
        sample_text = "The AlphaCentauri X1 rocket, by StarLeap Inc., had a successful suborbital test, reaching 120km. It aims for commercial space tourism by 2027, featuring a reusable hybrid engine."
        s1 = self.execute_step("generate_summary_with_local_llm",content_generator.generate_summary_local_llm,text_to_summarize=sample_text,max_length=50)
        if s1["status"] == "success" and s1["data"]: logger.info(f"Original: {sample_text}\nSummary: {s1['data']}")
        logger.info("\n--- Local LLM Test Summary Task Completed ---")
        self._print_history_summary()

    def run_scrape_forum_discussions_task(self, search_query: str, num_forums_to_scrape: int = 2, max_chars_per_page_for_summary: int = 2000, total_max_chars_for_summary:int = 6000):
        logger.info(f"\n--- Starting Scrape Forum Discussions for: '{search_query}' ---")
        logger.warning("IMPORTANT: Uses Botasaurus (Xvfb) and Ollama.")

        s_search = self.execute_step("find_forum_links",web_research.skill_perform_dynamic_search,query=f"{search_query} forum discussion",num_results=num_forums_to_scrape)
        if s_search["status"] == "failure" or not s_search["data"]:
            logger.error(f"Failed to find forum links. Error: {s_search['error_message']}. Aborting.")
            return

        links_to_scrape = [item["link"] for item in s_search["data"][:num_forums_to_scrape]]
        if not links_to_scrape: logger.info("No links to scrape."); return

        logger.info(f"Will scrape: {links_to_scrape}")
        scraped_results = self.execute_loop("scrape_forum_pages_loop",links_to_scrape,web_research.skill_extract_text_from_url,static_kwargs={"use_dynamic_fetch": True},item_kwarg_name="url")

        all_text = []
        scraped_details_report = []
        for i, res_dict in enumerate(scraped_results):
            link = links_to_scrape[i]
            status = res_dict["status"]
            data = res_dict["data"]
            err = res_dict["error_message"]
            text_len = len(data) if data else 0
            scraped_details_report.append(f"  - Scraped {link}: {status}, Length: {text_len}, Error: {err}")
            if status == "success" and data: all_text.append(data[:max_chars_per_page_for_summary])

        summary_text = "No summary generated (no content or LLM issue)."
        if all_text:
            combined = "\n\n--- Next Forum Page ---\n\n".join(all_text)
            if len(combined) > total_max_chars_for_summary: combined = combined[:total_max_chars_for_summary]

            sys_prompt = "Summarize the key topics, opinions, and consensus from the following forum discussion excerpts."
            s_summary = self.execute_step("summarize_forum_content",content_generator.generate_summary_local_llm,text_to_summarize=combined,max_length=300, custom_system_prompt=sys_prompt)
            if s_summary["status"] == "success" and s_summary["data"]: summary_text = s_summary["data"]
            if not content_generator.OLLAMA_IS_AVAILABLE() and s_summary["status"] == "success": summary_text += " (Placeholder - Ollama unavailable)"
        else:
            self.results_history["summarize_forum_content"] = {"status": "skipped", "data": "No content to summarize.", "error_message": None}

        logger.info(f"Generated Summary:\n{summary_text}")

        report_parts = [f"Report for query: '{search_query}'", "Links Found:"] + [str(s_search['data'])] + ["Scraping Details:"] + scraped_details_report + ["Summary:", summary_text]
        report_filename = f"forum_report_{search_query.replace(' ', '_')[:20]}.txt"
        self.execute_step("save_report",file_system.write_file,filepath=report_filename,content="\n".join(report_parts))
        logger.info(f"Report saved to workspace/{report_filename}")
        logger.info("\n--- Scrape Forum Discussions Task Completed ---")
        self._print_history_summary()

    def _print_history_summary(self):
        logger.info("\n--- Task Execution History Summary ---")
        for step, res_hist_item in self.results_history.items():
            if isinstance(res_hist_item, list) and step.startswith("scrape_forum_pages_loop"):
                 logger.info(f"  Loop '{step}': Processed {len(res_hist_item)} items.")
            elif isinstance(res_hist_item, list) and step.startswith("example_item_processing_loop"):
                 logger.info(f"  Loop '{step}': Processed {len(res_hist_item)} items.")
            elif isinstance(res_hist_item, dict):
                 logger.info(f"  Step '{step}': Status: {res_hist_item.get('status')}, Data (preview): {str(res_hist_item.get('data'))[:70]}..., Error: {res_hist_item.get('error_message')}")
            else:
                 logger.info(f"  Step '{step}': Unexpected result type in history: {type(res_hist_item)}")


def main():
    parser = argparse.ArgumentParser(description="Chimera Local Task Runner")
    parser.add_argument(
        "task_name",
        type=str,
        help="The name of the task to run (e.g., 'example', 'excel_lotto', 'scrape_forums')."
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Search query for tasks like 'scrape_forums'."
    )
    args = parser.parse_args()

    setup_workspace()
    orchestrator = TaskOrchestrator()

    if args.task_name == "example":
        orchestrator.run_example_task()
    elif args.task_name == "excel_lotto":
        orchestrator.run_excel_lotto_task()
    elif args.task_name == "dynamic_scrape_test":
        orchestrator.run_dynamic_scrape_test_task()
    elif args.task_name == "local_llm_test_summary":
        orchestrator.run_local_llm_test_summary_task()
    elif args.task_name == "scrape_forums":
        if not args.query:
            logger.error("ERROR: The 'scrape_forums' task requires a --query argument.")
            return
        orchestrator.run_scrape_forum_discussions_task(search_query=args.query)
    else:
        logger.error(f"Unknown task: {args.task_name}")
        print("Available tasks: example, excel_lotto, dynamic_scrape_test, local_llm_test_summary, scrape_forums")

if __name__ == "__main__":
    main()
