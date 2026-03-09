from flask import Flask
from application.database import db   #Step 3
app=None

def create_app():
    app=Flask(__name__)   #Step 1
    app.debug=True        #Step 1
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.sqlite3'   #Step 3
    db.init_app(app)
    app.app_context().push()    #Step 1
    app.secret_key = "placement_portal_secret" #secret key for session management
    return app

app = create_app()
from application.controllers import *    #Step 2
         

if __name__ == '__main__' :      #run the app only when invoked
    with app.app_context() :
        db.create_all()
        admin = User.query.filter_by(email='institute@login.com').first()         
        if admin is None :
            admin = User(username='INSTITUTE', email='institute@login.com', password='1234', role='admin', is_active=True, is_approved=True)
            db.session.add(admin)
            db.session.commit()
    app.run()


# Note : when we run this app module, it will create a proxy object as a current_app 
# which we can use later in other files and it will also avoid the circular import error, mapping happens at this point.