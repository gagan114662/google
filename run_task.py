import argparse
import os
import shutil
from app.tools import file_system, content_generator, web_scraper
from app.skills import web_research # reporting not needed for this new task yet

# Define the workspace directory
WORKSPACE_DIR = "workspace"

def setup_workspace():
    """Creates or cleans the workspace directory."""
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR)
    print(f"Workspace directory '{WORKSPACE_DIR}' created/cleaned.")

class TaskOrchestrator:
    def __init__(self):
        self.results_history = {} # To store results from steps

    def execute_step(self, step_name: str, function_to_call, **kwargs):
        """
        Executes a single step in a task, calls the provided function,
        and stores its result.
        """
        print(f"\n[Orchestrator] Executing step: {step_name}")
        try:
            if function_to_call is None:
                # This case was for the old example task, can be removed or adapted
                # For now, let's assume function_to_call is always provided for real tasks
                print(f"  Params: {kwargs}")
                result = f"No function provided for {step_name}, params: {kwargs}"
            elif step_name == "example_step_1" and function_to_call == print: # Specific handling for the modified example
                 function_to_call(f"  Params for {step_name}: {kwargs.get('message')}")
                 result = f"Printed message for {step_name}"
            elif step_name == "example_step_2" and function_to_call == print: # Specific handling for the modified example
                 function_to_call(f"  Params for {step_name}: {kwargs.get('message')}")
                 result = f"Printed message for {step_name}"
            else:
                # Call the actual tool/skill function
                print(f"  Calling function: {function_to_call.__name__} with params: {kwargs}")
                result = function_to_call(**kwargs)

            print(f"[Orchestrator] Step '{step_name}' completed. Result: {result}")
            self.results_history[step_name] = result
            return result
        except Exception as e:
            print(f"[Orchestrator] Error in step '{step_name}' calling {function_to_call.__name__ if function_to_call else 'None'} : {e}")
            self.results_history[step_name] = {"error": str(e)}
            return {"error": str(e)}

    def run_example_task(self):
        """
        A simple example task flow.
        This will be replaced by more specific task definitions later.
        """
        print("\n--- Starting Example Task ---")

        # Step 1: Example action
        step1_output = self.execute_step(
            "example_step_1",
            print, # Using print as a placeholder callable
            message="Executing example_step_1 with print function"
        )

        if isinstance(step1_output, dict) and "error" in step1_output:
            print("Task failed at step 1. Aborting.")
            return

        # Step 2: Another example action, potentially using output from step 1
        step2_output = self.execute_step(
            "example_step_2",
            print, # Using print as a placeholder callable
            message=f"Executing example_step_2, received from step 1: {step1_output}"
        )

        if isinstance(step2_output, dict) and "error" in step2_output:
            print("Task failed at step 2. Aborting.")
            return

        print("\n--- Example Task Completed ---")
        print("All step results:")
        for step, res in self.results_history.items():
            print(f"  {step}: {res}")

    def run_excel_lotto_task(self):
        """
        Task to generate an Excel spreadsheet with Italian lottery game information.
        """
        print("\n--- Starting Excel Lotto Task ---")

        # 1. Define lottery data (hardcoded for this example)
        lotto_data = {
            "headers": ["Game Name", "Description", "Draw Frequency", "Main Prize (Example)"],
            "rows": [
                ["Lotto", "Classic Italian number game", "3 times a week (Tue, Thu, Sat)", "€1,000,000+"],
                ["10eLotto", "Draws every 5 minutes, choose 10 numbers", "Every 5 minutes", "Up to €5,000,000"],
                ["MillionDAY", "Daily draw, pick 5 numbers to win €1,000,000", "Daily", "€1,000,000 (fixed)"]
            ]
        }

        # Step 1: Generate the Excel spreadsheet
        excel_filename = "italian_lottery_games.xlsx"
        step1_result = self.execute_step(
            step_name="generate_lottery_excel",
            function_to_call=content_generator.create_excel_spreadsheet,
            filename=excel_filename,
            data=lotto_data["rows"],
            headers=lotto_data["headers"]
        )

        if isinstance(step1_result, dict) and "error" in step1_result:
            print(f"Task failed at Excel generation. Error: {step1_result['error']}")
            return

        if not step1_result: # If function returned False
            print(f"Task failed at Excel generation (function returned False/None).")
            return

        print(f"Excel generation step successful. Expected file: {excel_filename}")

        # Step 2: Confirm file creation by listing files in workspace
        step2_result = self.execute_step(
            step_name="list_workspace_files",
            function_to_call=file_system.list_files,
            dirpath="." # List files in the root of the workspace
        )

        if isinstance(step2_result, dict) and "error" in step2_result:
            print(f"Task failed at listing files. Error: {step2_result['error']}")
            return

        print(f"Files in workspace: {step2_result}")
        if excel_filename in step2_result:
            print(f"SUCCESS: '{excel_filename}' found in workspace.")
        else:
            print(f"ERROR: '{excel_filename}' NOT found in workspace. Listing was: {step2_result}")

        print("\n--- Excel Lotto Task Completed ---")
        print("All step results:")
        for step, res in self.results_history.items():
            print(f"  {step}: {res}")

    def run_dynamic_scrape_test_task(self):
        """
        Task to test dynamic web scraping using Botasaurus via skills.
        """
        print("\n--- Starting Dynamic Scrape Test Task ---")
        print("IMPORTANT: This task uses Botasaurus and likely needs to be run with 'xvfb-run python run_task.py dynamic_scrape_test'")

        js_reliant_url = "http://quotes.toscrape.com/js/"
        output_text_file = "dynamic_scraped_quotes.txt"
        screenshot_file = "dynamic_scrape_screenshot.png"
        search_query = "inspirational quotes"

        # Step 1: Extract text dynamically
        step1_result = self.execute_step(
            step_name="extract_text_dynamically",
            function_to_call=web_research.skill_extract_text_from_url,
            url=js_reliant_url,
            use_dynamic_fetch=True
        )
        extracted_text = None
        if isinstance(step1_result, str):
            extracted_text = step1_result
            print(f"Dynamic text extraction successful (first 200 chars): {extracted_text[:200]}...")
        elif step1_result is None:
            print(f"Dynamic text extraction failed or returned None for {js_reliant_url}.")
        else: # Error dict
            print(f"Dynamic text extraction failed with error: {step1_result.get('error')}")
            # Optionally, decide if we should abort the task here
            # return

        # Step 2: Save extracted text to a file
        if extracted_text:
            step2_result = self.execute_step(
                step_name="save_extracted_text",
                function_to_call=file_system.write_file,
                filepath=output_text_file,
                content=extracted_text
            )
            if step2_result: # True if successful
                print(f"Extracted text saved to workspace/{output_text_file}")
            else:
                print(f"Failed to save extracted text.")
        else:
            print("Skipping save extracted text step as no text was extracted.")
            self.results_history["save_extracted_text"] = "Skipped"


        # Step 3: Perform a dynamic search
        step3_result = self.execute_step(
            step_name="perform_dynamic_search",
            function_to_call=web_research.skill_perform_dynamic_search,
            query=search_query,
            num_results=2
        )
        if isinstance(step3_result, list):
            print(f"Dynamic search for '{search_query}' returned {len(step3_result)} results:")
            for i, res in enumerate(step3_result):
                print(f"  {i+1}. {res.get('title', 'N/A')} - {res.get('link', 'N/A')}")
        else: # Error dict or unexpected
            print(f"Dynamic search failed or returned unexpected data: {step3_result}")

        # Step 4: Capture a screenshot (optional, can be slow)
        # Using the web_scraper tool directly for this example
        step4_result = self.execute_step(
            step_name="capture_screenshot",
            function_to_call=web_scraper.capture_screenshot_dynamic,
            url=js_reliant_url,
            output_filename=screenshot_file
        )
        if step4_result: # True if successful
            print(f"Screenshot captured and saved to workspace/{screenshot_file}")
        else:
            print(f"Failed to capture screenshot.")


        print("\n--- Dynamic Scrape Test Task Completed ---")
        print("All step results:")
        for step, res in self.results_history.items():
            print(f"  {step}: {res}")


def main():
    parser = argparse.ArgumentParser(description="Chimera Local Task Runner")
    parser.add_argument(
        "task_name",
        type=str,
        help="The name of the task to run (e.g., 'example', 'excel_lotto')."
    )
    # Add more arguments as needed, e.g., for input files, specific queries, etc.

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
    else:
        print(f"Unknown task: {args.task_name}")
        print("Available tasks: example, excel_lotto, dynamic_scrape_test, local_llm_test_summary")

if __name__ == "__main__":
    main()
