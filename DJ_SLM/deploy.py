import beam

# Define the application
app = beam.App(
    name="slm-defect-automation",
    cpu=4,
    memory="16Gi",
    gpu="T4",
)

# Define the files to be included in the deployment
app.mount_fs(
    ".",
    "src",
)

# Define the command to run the application
app.run(command="python orchestrator.py")
