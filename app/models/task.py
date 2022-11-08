from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    #def check_complete(self):
        # need to figure out how to reference in other functions
        #can I do that without including in parameters?
        

    def to_dict(self):
        if self.completed_at != None:
            check_status = True
        else:
            check_status = False

        return dict(
                    id=self.task_id,
                    title=self.title,
                    description=self.description,
                    is_completed=check_status
        )
