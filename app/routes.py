from flask import Blueprint, jsonify, request, make_response, abort
from app import db
from app.models.task import Task
from app.models.goal import Goal
from datetime import datetime
import requests
import os
#from dotenv import load_dotenv # not sure if I need this here, since it's in init 

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goals", __name__, url_prefix="/goals")

##-----------------------------------------------------------------##
##--------------------------Helper Functions-----------------------##
##-----------------------------------------------------------------##

## TO DO: Consolidate helper functions
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

#---------------------------------------------------------------#
#-------------------------TASK ROUTES---------------------------#
#---------------------------------------------------------------#

#-------------GET ALL TASKS------------#
@task_bp.route("", methods =["GET"])
def get_tasks():
    #maybe pull queries out into helper function to apply to multiple routes? (Goal/Tasks)
    sort_query = request.args.get("sort")

    if sort_query == 'asc':
        tasks = Task.query.order_by(Task.title.asc())
    elif sort_query == 'desc':
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
    tasks_response = [task.to_dict() for task in tasks]
    return make_response(jsonify(tasks_response), 200)

#-------------MAKE NEW TASK ------------#
@task_bp.route("", methods =["POST"])
def make_task():
    request_body = request.get_json()
    new_task = validate_new_task(request_body)
    db.session.add(new_task)
    db.session.commit()
    return make_response({"task":new_task.to_dict()}, 201)

#-------------GET SINGLE TASK ------------#
@task_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    task = validate_task(task_id)
    return make_response(dict(task=task.to_dict()), 200)                  

#-------------EDIT SINGLE TASK ------------#
@task_bp.route("/<task_id>", methods=["PUT"])
def edit_one_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    if "title" in request_body:
        task.title=request_body["title"]
    if "description" in request_body:
        task.description=request_body["description"]
    if "completed_at" in request_body:
        task.completed_at=request_body["completed_at"]
    
    db.session.commit()
    return(make_response({"task":task.to_dict()}, 200))

#-------------DELETE SINGLE TASK ------------#
@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_one_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()
    return make_response({"details": f'Task {task.task_id} "{task.title}" successfully deleted'},200)
    # Expected Response body Format Test Wave 1:
    # {"details": 'Task 1 "Go on my daily walk 🏞" successfully deleted'}

#-------------MARK TASK COMPLETE------------#
@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def check_task(task_id):
    task = validate_task(task_id)
    task.completed_at=datetime.now()
    db.session.commit()

    # Notify Slack of Task Completion - pull out into own function?
    URL = "https://slack.com/api/chat.postMessage"
    token = os.environ.get('SLACK_TOKEN')
    Headers = {"Authorization" : f'Bearer {token}'}
    params = {'channel':'task-notifications','text': f'Someone just completed the task {task.title}'}
    requests.post(URL,headers=Headers,params=params)

    return make_response({"task": task.to_dict()})

#------------MARK TASK INCOMPLETE-----------#
@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def uncheck_task(task_id):
    task = validate_task(task_id)
    task.completed_at=None
    db.session.commit()
    return make_response({"task": task.to_dict()})


#---------------------------------------------------------------#
#-------------------------GOAL ROUTES---------------------------#
#---------------------------------------------------------------#

#-------------GET ALL GOALS------------#
@goal_bp.route("", methods =["GET"])
def get_goals():
    sort_query = request.args.get("sort")

    if sort_query == 'asc':
        goals = Goal.query.order_by(Goal.title.asc())
    elif sort_query == 'desc':
        goals = Goal.query.order_by(Goal.title.desc())
    else:
        goals = Goal.query.all()

    goals_response = [goal.g_to_dict() for goal in goals]
    return make_response(jsonify(goals_response), 200)

#-------------MAKE NEW GOAL-------------#
@goal_bp.route("", methods =["POST"])
def make_goal():
    request_body = request.get_json()
    new_goal = validate_new_goal(request_body)
    db.session.add(new_goal)
    db.session.commit()
    return make_response({"goal":new_goal.g_to_dict()}, 201)

#-------------GET SINGLE GOAL------------#
@goal_bp.route("/<goal_id>", methods=["GET"])
def one_goal(goal_id):
    goal = validate_goal(goal_id)
    if request.method == 'GET':
        return make_response(dict(goal=goal.g_to_dict()), 200)

#-------------EDIT SINGLE GOAL-------------#
@goal_bp.route("/<goal_id>", methods=["PUT"])
def edit_goal(goal_id):
    goal = validate_goal(goal_id)
    request_body = request.get_json()
    if "title" in request_body:
        goal.title=request_body["title"]
    if "description" in request_body:
        goal.description=request_body["description"]

    db.session.commit()
    return(make_response({"goal":goal.g_to_dict()}, 200))

#-------------DELETE SINGLE GOAL-------------#
@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = validate_goal(goal_id)
    db.session.delete(goal)
    db.session.commit()
    return make_response({"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'},200)

#---------------------------------------------------------------#
#-----------------------NESTED ROUTES---------------------------#
#---------------------------------------------------------------#
#would be nice to have helper function to dictionary-ify a list of tasks
#or.... I could just somehow have the goal store or output them in the correct format

#-------------GET ALL GOAL'S TASKs-------------#

@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    goal = validate_goal(goal_id)
    #need dictionary formatted task to be returned, not raw task
    goal_response = goal.g_to_dict_tasks()
    return make_response(jsonify(goal_response), 200)
    # need to get it listing more than one task!

#---------------ADD TASKS TO GOAL--------------#
@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def add_tasks(goal_id):
    goal = validate_goal(goal_id)
    request_body = request.get_json()
    if "task_ids" in request_body:
        for id in request_body["task_ids"]:
            task = validate_task(id)
            task.goal_id=goal.goal_id       
    else:
        abort(make_response({"details": "Invalid data"},400))
    db.session.commit()

    #confirm that tasks were linked in database- there has to be a better way to check this
    new_goal_tasks = []
    for id in request_body["task_ids"]:
        if task.goal_id == goal.goal_id:
            new_goal_tasks.append(id)

    return make_response({"id": goal.goal_id, "task_ids": new_goal_tasks},200)


    # Do we assign the goal id to all the listed tasks, or do we assign the task list to goal?
    # tasks have a goal id value, which is an integer, so probably the latter
    # then need to figure out how to retrieve the task IDs from goal 
    # Desired response message:
    # {
    #  "id": 1,
    #   "task_ids": [1, 2, 3]
    #   },200)