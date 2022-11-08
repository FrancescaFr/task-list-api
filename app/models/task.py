from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    
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
                    is_complete=check_status
                )
        
