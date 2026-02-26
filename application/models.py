from .database import db             
#context of application is root directory, with dot, it will look in current directory
#no dot means it'll look in root directory with



class User(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)    # 'admin', 'student', 'company'
    is_active = db.Column(db.Boolean, default=True)

    #Student specific fields
    resume = db.Column(db.String(200))

    #Company specific fields
    company_name = db.Column(db.String(150))
    website = db.Column(db.String(200))
    hr_contact = db.Column(db.String(150))
    is_approved = db.Column(db.Boolean, default=False)

    # Relationships
    applications = db.relationship('Application', backref='student', cascade='all, delete')  #If student is deleted → applications also deleted.
    drives = db.relationship('PlacementDrive', backref='company', cascade="all, delete")


      
class PlacementDrive(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)                                     #it can be long, so Text for long paragraphs
    eligibility_criteria = db.Column(db.String(200), nullable=False)
    application_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Upcoming')                                     # 'Upcoming', 'Closed'
    applications = db.relationship('Application', backref='drive', cascade='all, delete')     #If drive is deleted → applications also deleted.



class Application(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    application_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='Applied')                                             # 'Applied', 'Shortlisted', 'Selected', 'Rejected'
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),)     #to prevent duplicate applications