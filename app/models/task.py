from app import db
## found an error where updating the string character restriction does not change the database values
## tried everything... dropped the database, rebuilt, changed version files...everything
class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")

    #def check_complete(self):
        # would like to be able to reference in other class methods
        # can I do that without including in arguments?

    def to_dict(self):
        if self.completed_at != None:
            check_status = True
        else:
            check_status = False

        return dict(
                    id=self.task_id,
                    title=self.title,
                    description=self.description,
                    goal_id=self.goal_id,
                    is_complete=check_status
                )
        
