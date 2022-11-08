from flask import Blueprint, jsonify, request, make_response, abort
from app import db
from app.models.task import Task
from app.models.goal import Goal

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
                        completed_at=request_body["completed_at"])
    except:
        abort(make_response({"details": "Invalid data"},400))
    return new_task


@task_bp.route("", methods =["GET","POST"])
def handle_tasks():
    if request.method == 'GET':
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
 