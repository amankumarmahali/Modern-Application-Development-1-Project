from flask import Flask, render_template, request, redirect, session
from flask import current_app as app
from .models import *

from datetime import datetime
 



@app.route("/login", methods=['GET', 'POST'])
def login() :
    if request.method == 'POST' :
        username = request.form['username']
        pwd = request.form.get('pwd')
        this_user = User.query.filter_by(username=username).first()
        if this_user :

            if not this_user.is_active :     #if user is not active, then they should not login
                return render_template("inactive.html")
            
            if this_user.password == pwd :

                session['user_id'] = this_user.id
                session['role'] = this_user.role




                if this_user.role == "admin" :
                    return redirect("/admin")
                
                elif this_user.role == "company" :
                    if not this_user.is_approved :
                        return render_template("not_approved.html")
                    return redirect("/company")
                
                elif this_user.role == "student" :
                    return redirect("/student")
                
            else :
                return render_template("incorrect_p.html")
        else :
            return render_template("not_found.html")                 
    return render_template("login.html")



@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST' :
        username = request.form.get('username')
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        role = request.form.get('role')            
        user_name = User.query.filter_by(username=username).first()
        user_email = User.query.filter_by(email=email).first()
        
        if user_name or user_email:
            return render_template("already_found.html")  
        else :
            new_user = User(
                username=username,          #LHS : Attribute name ; RHS : value
                email=email,
                password=pwd,
                role=role,
                is_active=True,
                is_approved=False if role == 'company' else True)  
            db.session.add(new_user)
            db.session.commit()    
            return redirect("/login")
    return render_template("register.html")



@app.route("/admin")
def admin() :

    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect("/login")

    # this_user = User.query.filter_by(role='admin').first()  #we have only one admin, so we can use first()
    this_user = User.query.get(session['user_id'])

    all_reg_comp = User.query.filter_by(role='company').all()                         #to get all the registered companies
    all_reg_students = User.query.filter_by(role='student').all()                     #to get all the registered students
    all_comp_app = User.query.filter_by(role='company', is_approved=False).all()      #to get all the applications of the Companies
    all_ongoing_drives = PlacementDrive.query.filter_by(status='Upcoming').all()      #to get all the ongoing drives
    all_std_app = Application.query.all()                                             #to get all the applications of the Students
    return render_template("admin_dash.html", this_user=this_user, all_reg_comp=all_reg_comp, all_reg_students=all_reg_students, all_comp_app=all_comp_app, all_ongoing_drives=all_ongoing_drives, all_std_app=all_std_app)



@app.route("/student")
def student() :

    if 'user_id' not in session or session.get('role') != 'student':
        return redirect("/login")
    
    # this_user = User.query.get(user_id)
    this_user = User.query.get(session['user_id'])

    organizations = User.query.filter_by(role='company', is_approved=True).all()         #to get all the approved companies
    applied_drives = Application.query.filter_by(student_id=this_user.id).all()          #to get all the drives applied by the student
    return render_template("std_dash.html", this_user=this_user, organizations=organizations, applied_drives=applied_drives)



@app.route("/company")
def company() :
    
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect("/login")

    # this_user = User.query.get(user_id)
    this_user = User.query.get(session['user_id'])
    upcoming_drives = PlacementDrive.query.filter_by(company_id=this_user.id, status='Upcoming').all()        #to get all the upcoming drives created by the company
    closed_drives = PlacementDrive.query.filter_by(company_id=this_user.id, status='Closed').all()            #to get all the closed drives created by the company
    return render_template("company_dash.html", this_user=this_user, upcoming_drives=upcoming_drives, closed_drives=closed_drives)



@app.route("/create", methods=['GET', 'POST'])
def create_drive() :
    
    if 'user_id' not in session:
        return redirect("/login")
    if session.get('role') != 'company':
        return render_template("not_approved.html")
    
    company_id  = User.query.get(session['user_id'])
    
    if not company.is_approved :
        return render_template("not_approved.html")




    if request.method == 'POST' :
        name = request.form.get('name')
        title = request.form.get('title')
        desc = request.form.get('desc')
        elig = request.form.get('elig')
        deadline_str = request.form.get('deadline')
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()   #to convert the string input to a date object
        # company_id = session.get('user_id')

        new_drive = PlacementDrive(
            company_id=company_id,
            name=name,
            job_title=title,
            job_description=desc,
            eligibility_criteria=elig,
            application_deadline=deadline,
            status='Upcoming'
        )
        db.session.add(new_drive)
        db.session.commit()
        return redirect("/company")
    return render_template("company_create_drive.html")



 

# @app.route()  
# 1. from models import * -> will look for this in the root directory
# 2. from .models import * -> will look for this in the current directory
# 3. from application.models import * -> controllers.py will think that there is one more application 
# folder in the root directory(application folder) with respect to the controllers.py