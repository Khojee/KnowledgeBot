import sqlite3
import json
import logging
from datetime import datetime

DATABASE_FILE = "bot_database.db"

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Table for storing chat history per user
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                chat_id INTEGER PRIMARY KEY,
                history TEXT NOT NULL
            )
        """)
        # Table for logging user feedback from votes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_log (
                interaction_id TEXT PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                vote TEXT,
                timestamp DATETIME NOT NULL
            )
        """)
        conn.commit()
    logging.info("Database initialized successfully.")


def log_interaction(interaction_id: str, chat_id: int, question: str, answer: str):
    """Logs a new question-answer interaction before a vote is cast."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback_log (interaction_id, chat_id, question, answer, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (interaction_id, chat_id, question, answer, datetime.now()))
        conn.commit()

def update_vote(interaction_id: str, vote: str):
    """Updates an interaction record with the user's vote."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE feedback_log
            SET vote = ?
            WHERE interaction_id = ?
        """, (vote, interaction_id))
        conn.commit()
    logging.info(f"Vote '{vote}' recorded for interaction {interaction_id}")