#!/bin/bash
cd /path/to/defect-triage
source venv/bin/activate
python src/retrain.py >> logs/retrain.log 2>&1
