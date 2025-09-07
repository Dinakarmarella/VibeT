"""
Main entry point for the Automated Content Agent.

This script initializes the necessary components and starts the orchestration process.
"""

from agent.orchestrator import Orchestrator

def main():
    """
    Initializes and runs the agent.
    """
    print("Starting Automated Content Agent...")
    
    orchestrator = Orchestrator(config_path='config.yaml')
    
    # Example task execution. This would be triggered by a scheduler in production.
    orchestrator.execute_task('daily_youtube_summary')
    
    print("Agent run finished.")

if __name__ == "__main__":
    main()
