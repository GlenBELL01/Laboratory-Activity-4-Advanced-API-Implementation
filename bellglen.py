from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
import os
import logging

# Load .env variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Key from .env
API_KEY = os.getenv("LAB4_API_KEY")
API_KEY_NAME = "GLEN_LAB4_api_key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# FastAPI Application
app = FastAPI()

# Sample data storage
tasks_data = [
    {"Id": 1, "Title": "Complete Lab Activity", "Description": "Finish Lab Activity 2", "done": False}
]

# Task model for creating a new task
class NewTask(BaseModel):
    Title: str = Field(..., min_length=1, description="Task Title")
    Description: Optional[str] = Field(None, description="Task Description")
    done: bool = False

# Task model for updating an existing task
class UpdateTask(BaseModel):
    Title: Optional[str] = Field(None, min_length=1, description="Task Title")
    Description: Optional[str] = Field(None, description="Task Description")
    done: Optional[bool] = None

# Function to find task by ID
def get_task_by_id(task_id: int):
    logger.info(f"Searching for task with ID: {task_id}")
    task = next((task for task in tasks_data if task["Id"] == task_id), None)
    if task:
        logger.info(f"Task found: {task}")
    else:
        logger.warning(f"Task with ID {task_id} not found.")
    return task

# Dependency to check API Key
def validate_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        logger.error("Unauthorized access attempt detected.")
        raise HTTPException(status_code=401, detail="Unauthorized")
    logger.info("API key validation successful.")

# Version 1 Endpoints
@app.get("/v1/tasks/{task_id}")
def read_task_v1(task_id: int):
    """Get a task by ID for version 1."""
    logger.info(f"GET request received (v1) for task ID: {task_id}")
    if task_id <= 0:
        logger.error("Invalid task ID provided.")
        raise HTTPException(status_code=400, detail="Task ID must be a positive integer")
    task = get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    return {"Status": "Success", "Task": task}

@app.post("/v1/tasks", status_code=201)
def add_task_v1(new_task: NewTask):
    """Add a task for version 1."""
    logger.info("POST request received (v1) to add a new task.")
    new_id = len(tasks_data) + 1
    task_to_add = {
        "Id": new_id,
        "Title": new_task.Title,
        "Description": new_task.Description,
        "done": new_task.done
    }
    tasks_data.append(task_to_add)
    logger.info(f"Task added successfully (v1): {task_to_add}")
    return {"Status": "Success", "Task Added": task_to_add}

@app.patch("/v1/tasks/{task_id}")
def modify_task_v1(task_id: int, updated_task: UpdateTask):
    """Update a task for version 1."""
    logger.info(f"PATCH request received (v1) to update task ID: {task_id}")
    if task_id <= 0:
        logger.error("Invalid task ID provided.")
        raise HTTPException(status_code=400, detail="Task ID must be a positive integer")
    task = get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    if updated_task.Title is not None:
        task["Title"] = updated_task.Title
    if updated_task.Description is not None:
        task["Description"] = updated_task.Description
    if updated_task.done is not None:
        task["done"] = updated_task.done
    logger.info(f"Task updated successfully (v1): {task}")
    return {"Status": "Success", "Message": "Task Updated Successfully"}

@app.delete("/v1/tasks/{task_id}")
def remove_task_v1(task_id: int):
    """Delete a task for version 1."""
    logger.info(f"DELETE request received (v1) for task ID: {task_id}")
    if task_id <= 0:
        logger.error("Invalid task ID provided.")
        raise HTTPException(status_code=400, detail="Task ID must be a positive integer")
    task = get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    tasks_data.remove(task)
    logger.info(f"Task with ID {task_id} deleted successfully (v1).")
    return {"Status": "Success", "Message": f"Task with ID {task_id} deleted"}

# Version 2 Endpoints
@app.get("/v2/tasks/{task_id}", dependencies=[Depends(validate_api_key)])
def read_task_v2(task_id: int):
    """Get a task by ID for version 2."""
    return read_task_v1(task_id)

@app.post("/v2/tasks", dependencies=[Depends(validate_api_key)], status_code=201)
def add_task_v2(new_task: NewTask):
    """Add a task for version 2."""
    return add_task_v1(new_task)

@app.patch("/v2/tasks/{task_id}", dependencies=[Depends(validate_api_key)])
def modify_task_v2(task_id: int, updated_task: UpdateTask):
    """Update a task for version 2."""
    return modify_task_v1(task_id, updated_task)

@app.delete("/v2/tasks/{task_id}", dependencies=[Depends(validate_api_key)])
def remove_task_v2(task_id: int):
    """Delete a task for version 2."""
    return remove_task_v1(task_id)
