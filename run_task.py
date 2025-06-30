import argparse
import os
import shutil
from app.tools import file_system, content_generator # web_scraper not needed for this task
# from app.skills import web_research, reporting # Skills not directly used in this simple task yet

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
    else:
        print(f"Unknown task: {args.task_name}")
        print("Available tasks: example, excel_lotto")

if __name__ == "__main__":
    main()
