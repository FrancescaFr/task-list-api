from flask import Blueprint, jsonify, request, make_response, abort
from app import db
from app.models.task import Task
from app.models.goal import Goal
from datetime import datetime, time
import requests
import os
from dotenv import load_dotenv

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goals", __name__, url_prefix="/goals")

def validate_task(id):
    try:
        id = int(id)
    except:
        abort(make_response({"message": f"Task {id} is invalid"}, 400))

    task = Task.query.get(id)
    if not task:
        abort(make_response({"message": f"Task {id} not found"}, 404))
    return task


def validate_new_task(request_body):
    try:
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        #completed_at=request_body["completed_at"]
                        )
    except:
        abort(make_response({"details": "Invalid data"},400))
    return new_task


@task_bp.route("", methods =["GET","POST"])
def handle_tasks():
    if request.method == 'GET':

        sort_query = request.args.get("sort")

        if sort_query == 'asc':
            tasks = Task.query.order_by(Task.title.asc())
        elif sort_query == 'desc':
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        tasks_response = [task.to_dict() for task in tasks]
        return make_response(jsonify(tasks_response), 200)

    if request.method == 'POST':
        request_body = request.get_json()
        new_task = validate_new_task(request_body)
        db.session.add(new_task)
        db.session.commit()
        return make_response({"task":new_task.to_dict()}, 201)


@task_bp.route("/<task_id>", methods=["GET","PUT","DELETE"])
def one_task(task_id):
    task = validate_task(task_id)
    if request.method == 'GET':
        return make_response(dict(task=task.to_dict()), 200)
    
    if request.method == 'PUT':
        request_body = request.get_json()
        if "title" in request_body:
            task.title=request_body["title"]
        if "description" in request_body:
            task.description=request_body["description"]
        if "completed_at" in request_body:
            task.completed_at=request_body["completed_at"]
        

        db.session.commit()
        return(make_response({"task":task.to_dict()}, 200))

    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return make_response({"details": f'Task {task.task_id} "{task.title}" successfully deleted'},200)

        # Expected Response body Format Test Wave 1:
        # {"details": 'Task 1 "Go on my daily walk 🏞" successfully deleted'}

@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def check_task(task_id):
    task = validate_task(task_id)
    task.completed_at=datetime.now()
    db.session.commit()

    # Notify Slack of Task Completion
    URL = "https://slack.com/api/chat.postMessage"
    token = os.environ.get('SLACK_TOKEN')
    Headers = {"Authorization" : f'Bearer {token}'}
    params = {'channel':'task-notifications','text': f'Someone just completed the task {task.title}'}
    requests.post(URL,headers=Headers,params=params)

    return make_response({"task": task.to_dict()})

@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def uncheck_task(task_id):
    task = validate_task(task_id)
    task.completed_at=None
    db.session.commit()
    return make_response({"task": task.to_dict()})


#####################################################
#------------------GOAL ROUTES----------------------#
#####################################################


def validate_goal(id):
    try:
        id = int(id)
    except:
        abort(make_response({"message": f"Goal {id} is invalid"}, 400))

    goal = Goal.query.get(id)
    if not goal:
        abort(make_response({"message": f"Goal {id} not found"}, 404))
    return goal

def validate_new_goal(request_body):
    try:
        new_goal = Goal(title=request_body["title"])
    except:
        abort(make_response({"details": "Invalid data"},400))
    return new_goal


@goal_bp.route("", methods =["GET","POST"])
def handle_goals():
    if request.method == 'GET':

        sort_query = request.args.get("sort")

        if sort_query == 'asc':
            goals = Goal.query.order_by(Goal.title.asc())
        elif sort_query == 'desc':
            goals = Goal.query.order_by(Goal.title.desc())
        else:
            goals = Goal.query.all()
        goals_response = [goal.g_to_dict() for goal in goals]
        return make_response(jsonify(goals_response), 200)

    if request.method == 'POST':
        request_body = request.get_json()
        new_goal = validate_new_goal(request_body)
        db.session.add(new_goal)
        db.session.commit()
        return make_response({"goal":new_goal.g_to_dict()}, 201)


@goal_bp.route("/<goal_id>", methods=["GET","PUT","DELETE"])
def one_goal(goal_id):
    goal = validate_goal(goal_id)
    if request.method == 'GET':
        return make_response(dict(goal=goal.g_to_dict()), 200)
    
    if request.method == 'PUT':
        request_body = request.get_json()
        if "title" in request_body:
            goal.title=request_body["title"]

        db.session.commit()
        return(make_response({"goal":goal.g_to_dict()}, 200))

    if request.method == 'DELETE':
        db.session.delete(goal)
        db.session.commit()
        return make_response({"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'},200)

