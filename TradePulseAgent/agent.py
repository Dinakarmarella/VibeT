import schedule
import time
import logging
from tasks import run_agent_task

# --- 1. Logging Setup ---
logging.basicConfig(filename='agent.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- 2. Scheduler ---
def main():
    """
    Main function to schedule and run the agent.
    """
    logging.info("--- Social Media Agent Started ---")
    
    # Run the task once immediately on startup
    run_agent_task()
    
    # Schedule the task to run every 3 hours
    schedule.every(3).hours.do(run_agent_task)
    
    logging.info("Agent scheduled to run every 3 hours. Waiting for next run...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
