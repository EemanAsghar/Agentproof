import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from demo_agent.main import app as agent_app
from dashboard.app import app as dashboard_app

app = FastAPI()
app.mount("/agent", agent_app)
app.mount("/", dashboard_app)
