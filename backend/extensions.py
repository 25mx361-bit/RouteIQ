"""
extensions.py — Shared Flask extension instances.

Instantiate extensions here (without app) to avoid circular imports.
The create_app() factory calls init_app() on each to bind them to the app.
"""
from flask_pymongo import PyMongo
from apscheduler.schedulers.background import BackgroundScheduler

# MongoDB client — use via `mongo.db` inside request context
mongo = PyMongo()

# Background scheduler for periodic data collection jobs
scheduler = BackgroundScheduler()
