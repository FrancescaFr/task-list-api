from app import db

class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", back_populates="goal",lazy=True)

#also maybe I should pull these dictionaries out!
#only currently appending one task from tasks 
    def g_to_dict_tasks(self):
        task_list =[]
        for task in self.tasks:
            task_list.append(task_to_dict(task))

        return dict(
                id=self.goal_id,
                title=self.title,
                tasks=task_list
            )

    def g_to_dict(self):
        return dict(
                    id=self.goal_id,
                    title=self.title
                )

def task_to_dict(task):
            if task.completed_at != None:
                check_status = True
            else:
                check_status = False

            return dict(
                        id=task.task_id,
                        title=task.title,
                        description=task.description,
                        goal_id=task.goal_id,
                        is_complete=check_status
                    )