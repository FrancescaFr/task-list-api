import os
from datetime import datetime

import requests
from flask import Blueprint, abort, jsonify, make_response, request

from app import db
from app.models.goal import Goal
from app.models.task import Task

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goals", __name__, url_prefix="/goals")

##-----------------------------------------------------------------##
##--------------------------Helper Functions-----------------------##
##-----------------------------------------------------------------##

def validate_item(cls,id):
    try:
        id = int(id)
    except:
        abort(make_response({"message": f"{cls.__name__} {id} is invalid"}, 400))

    item = cls.query.get(id)
    if not item:
        abort(make_response({"message": f"{cls.__name__} {id} not found"}, 404))

    return item

def validate_new_item(cls,request_body):
    try:  
        if cls == Task:
            new_item = cls(title=request_body["title"],
                           description=request_body["description"]
                        )
        else:
             new_item = cls(title=request_body["title"])
    except:
        abort(make_response({"details": "Invalid data"},400))

    return new_item

def post_to_slack(task):
    URL = "https://slack.com/api/chat.postMessage"
    token = os.environ.get('SLACK_TOKEN')
    Headers = {"Authorization" : f'Bearer {token}'}
    params = {'channel':'task-notifications',
              'text': f'Someone just completed the task {task.title}'
            }

    requests.post(URL,headers=Headers,params=params)

def task_to_goal(task_id,goal):
    task = validate_item(Task,task_id)
    task.goal_id=goal.goal_id

    return task_id

def to_dict(self,list_tasks=False):
    item_dict = {} 

    if self.__class__ == Task:
        item_dict["id"]=self.task_id
        item_dict["title"]=self.title
        item_dict["description"]=self.description

        if self.completed_at != None:
            item_dict["is_complete"]=True
        else:
            item_dict["is_complete"]=False

        if self.goal_id:
            item_dict["goal_id"]=self.goal_id
        
    if self.__class__ == Goal:
        item_dict["id"]=self.goal_id
        item_dict["title"]=self.title

        if list_tasks==True:
            task_list = []
            for task in self.tasks:
                task_list.append(to_dict(task)) # recursion baby!
            item_dict["tasks"]=task_list

    return item_dict

def query_filter(cls):
    sort_query = request.args.get("sort")
    filter_query = request.args.get("filter")
    by = request.args.get("by")

    if sort_query:
        if sort_query == 'asc' or sort_query != 'desc':
            if not by or by == 'title':
                order = cls.title.asc
            if by == 'goal':
                order = cls.goal_id.asc
            if by == 'date':
                order = cls.completed_at.asc
        if sort_query == 'desc':
            if not by or by == 'title':
                order = cls.title.desc
            if by == 'goal':
                order = cls.goal_id.desc
            if by == 'date':
                order = cls.completed_at.desc

        results = cls.query.order_by(order())
    else:
        results = cls.query

    if filter_query:
        if filter_query == 'todo':
            results = results.filter(Task.completed_at == None)
        if filter_query == 'done':
            results = results.filter(Task.completed_at != None)

    return results

#---------------------------------------------------------------#
#-------------------------TASK ROUTES---------------------------#
#---------------------------------------------------------------#

#-------------GET ALL TASKS------------#
@task_bp.route("", methods =["GET"])
def get_tasks():
    tasks = query_filter(Task)
    tasks_response = [to_dict(task) for task in tasks]

    return make_response(jsonify(tasks_response), 200)

#-------------MAKE NEW TASK ------------#
@task_bp.route("", methods =["POST"])
def make_task():
    request_body = request.get_json()
    new_task = validate_new_item(Task,request_body)
    db.session.add(new_task)
    db.session.commit()

    return make_response({"task":to_dict(new_task)}, 201)

#-------------GET SINGLE TASK ------------#
@task_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    task = validate_item(Task,task_id)

    return make_response(dict(task=to_dict(task)), 200)                  

#-------------EDIT SINGLE TASK ------------#
@task_bp.route("/<task_id>", methods=["PUT"])
def edit_one_task(task_id):
    task = validate_item(Task,task_id)
    request_body = request.get_json()

    if "title" in request_body:
        task.title=request_body["title"]
    if "description" in request_body:
        task.description=request_body["description"]
    if "completed_at" in request_body:
        task.completed_at=request_body["completed_at"]

    db.session.commit()

    return(make_response({"task":to_dict(task)}, 200))

#-------------DELETE SINGLE TASK ------------#
@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_one_task(task_id):
    task = validate_item(Task,task_id)

    db.session.delete(task)
    db.session.commit()

    return make_response({"details": f'Task {task.task_id} "{task.title}" successfully deleted'},200)

#-------------MARK TASK COMPLETE------------#
@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def check_task(task_id):
    task = validate_item(Task,task_id)
    task.completed_at=datetime.now()

    db.session.commit()

    post_to_slack(task)

    return make_response({"task": to_dict(task)})

#------------MARK TASK INCOMPLETE-----------#
@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def uncheck_task(task_id):
    task = validate_item(Task,task_id)
    task.completed_at=None

    db.session.commit()

    return make_response({"task": to_dict(task)})

#---------------------------------------------------------------#
#-------------------------GOAL ROUTES---------------------------#
#---------------------------------------------------------------#

#-------------GET ALL GOALS------------#
@goal_bp.route("", methods =["GET"])
def get_goals():
    goals = query_filter(Goal)
    goals_response = [to_dict(goal) for goal in goals]

    return make_response(jsonify(goals_response), 200)

#-------------MAKE NEW GOAL-------------#
@goal_bp.route("", methods =["POST"])
def make_goal():
    request_body = request.get_json()
    new_goal = validate_new_item(Goal,request_body)

    db.session.add(new_goal)
    db.session.commit()

    return make_response({"goal":to_dict(new_goal)}, 201)

#-------------GET SINGLE GOAL------------#
@goal_bp.route("/<goal_id>", methods=["GET"])
def one_goal(goal_id):
    goal = validate_item(Goal,goal_id)

    return make_response(dict(goal=to_dict(goal)), 200)

#-------------EDIT SINGLE GOAL-------------#
@goal_bp.route("/<goal_id>", methods=["PUT"])
def edit_goal(goal_id):
    goal = validate_item(Goal,goal_id)
    request_body = request.get_json()

    if "title" in request_body:
        goal.title=request_body["title"]
    if "description" in request_body:
        goal.description=request_body["description"]

    db.session.commit()

    return(make_response({"goal":to_dict(goal)}, 200))

#-------------DELETE SINGLE GOAL-------------#
@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = validate_item(Goal,goal_id)

    db.session.delete(goal)
    db.session.commit()

    return make_response({"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'},200)

#---------------------------------------------------------------#
#-----------------------NESTED ROUTES---------------------------#
#---------------------------------------------------------------#

#-------------GET ALL GOAL'S TASKs-------------#

@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    goal = validate_item(Goal,goal_id)
    goal_response = to_dict(goal,list_tasks=True)

    return make_response(jsonify(goal_response), 200)

#---------------ADD TASKS TO GOAL--------------#
@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def add_tasks(goal_id):
    goal = validate_item(Goal,goal_id)
    request_body = request.get_json()
    
    if "task_ids" in request_body:
        task_list = [task_to_goal(id,goal) for id in request_body["task_ids"]]
    else:
        abort(make_response({"details": "Invalid data"},400))

    db.session.commit()

    return make_response({"id": goal.goal_id, "task_ids": task_list},200)

