import subprocess
import yaml
import os

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
config = yaml.safe_load(open(config_path))

def retrain():
    src_dir = os.path.dirname(__file__)
    preprocess_script_path = os.path.join(src_dir, "preprocess.py")
    train_script_path = os.path.join(src_dir, "train.py")

    # Paths for raw and processed data are relative to the project root (DIJI_AI folder)
    # So, we need to pass them as is, and the subprocesses will handle them correctly
    # if they also load config.yaml with the correct path.
    subprocess.run(["python", preprocess_script_path, config["paths"]["raw_data"], config["paths"]["processed_data"]], cwd=os.path.dirname(src_dir))
    subprocess.run(["python", train_script_path], cwd=os.path.dirname(src_dir))

if __name__ == "__main__":
    retrain()
