from flask import Flask, render_template, request, redirect, session, url_for
from flask import current_app as app
from .models import *
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')





@app.route("/")
def home():
    return render_template("home.html")



@app.route("/login", methods=['GET', 'POST'])
def login() :
    if request.method == 'POST' :
        username = request.form.get('username')
        pwd = request.form.get('pwd')

        this_user = User.query.filter_by(username=username).first()
        if this_user :

            if not this_user.is_active :     #if user is not active, then they should not login
                return render_template("inactive.html")
            
            if this_user.password == pwd :

                session['user_id'] = this_user.id
                session['role'] = this_user.role
 
                if this_user.role == "admin" :
                    return redirect(url_for('admin'))
                
                elif this_user.role == "company" :
                    if not this_user.is_approved :                    #if company is not approved, then they should not login
                        return render_template("not_approved.html")
                    return redirect(url_for('company'))
                
                elif this_user.role == "student" :
                    return redirect(url_for('student'))
                
            else :
                return render_template("incorrect_p.html")
            
        else :
            return render_template("not_found.html") 
                        
    return render_template("login.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))



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
            return redirect(url_for('login'))
    return render_template("register.html")



#################### ROUTES FOR ADMIN ####################################################################################


@app.route("/admin")
def admin() :
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    this_user = User.query.get(session['user_id'])

    all_reg_comp = User.query.filter_by(role='company', is_active=True).all()                #to get all the registered companies
    blacklisted_company = User.query.filter_by(role='company', is_active=False).all()        #to get all the blacklisted companies
    all_reg_student = User.query.filter_by(role='student', is_active=True).all()             #to get all the registered students
    blacklisted_students = User.query.filter_by(role='student', is_active=False).all()       #to get all the blacklisted students
    all_comp_app = User.query.filter_by(role='company', is_approved=False).all()             #to get all the applications of the Companies to get approved
    all_ongoing_drives = PlacementDrive.query.filter_by(status='upcoming').all()             #to get all the ongoing drives
    all_std_app = Application.query.all()                                                    #to get all the applications of the Students
    all_closed_drives = PlacementDrive.query.filter_by(status='closed').all()                #to get all the closed drives
    return render_template("admin_dash.html",
                           this_user=this_user,
                           all_reg_comp=all_reg_comp,
                           blacklisted_company=blacklisted_company,
                           all_reg_student=all_reg_student,
                           blacklisted_students=blacklisted_students,
                           all_comp_app=all_comp_app,
                           all_ongoing_drives=all_ongoing_drives,
                           all_std_app=all_std_app,
                           all_closed_drives=all_closed_drives
                           )



@app.route("/search")
def search():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    this_user = User.query.get(session['user_id'])
    search_word = request.args.get('search')
    key = request.args.get('key')
    results = []

    if key == 'student' :
        results = User.query.filter(User.role =='student', User.username.ilike(f"%{search_word}%")).all()
    elif key == 'company' :
        results = User.query.filter(User.role =='company', User.username.ilike(f"%{search_word}%")).all()
    
    return render_template("search_results.html", this_user=this_user, search_word=search_word, key=key, results=results)
        


@app.route("/admin/summary")
def ad_summary():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    this_user = User.query.get(session['user_id'])

    applied=len(Application.query.filter_by(status='Applied').all())
    shortlisted=len(Application.query.filter_by(status='Shortlisted').all())
    selected = len(Application.query.filter_by(status='Selected').all())
    rejected=len(Application.query.filter_by(status='Rejected').all())

    total_application = (applied + shortlisted + selected + rejected)
    drive = len(PlacementDrive.query.all())
    student = len(User.query.filter_by(role='student').all())
    company = len(User.query.filter_by(role='company').all())


#pie_chart
    labels = ['Applied', 'Shortlisted', 'Selected', 'Rejected']
    sizes = [applied, shortlisted, selected, rejected]
    colors = ["yellow",  "blue", "green", "red"]
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.savefig("placement-portal-application/static/pie.png")
    plt.clf()

#bar_chart
    labels = ['Students', 'Companies', 'Drives', 'Applications']
    sizes = [student, company, drive, total_application]
    plt.bar(labels, sizes)
    plt.xlabel('Entities')
    plt.ylabel('Count')
    plt.savefig("placement-portal-application/static/bar.png")
    plt.clf()

    return render_template("admin_summary.html",
                           this_user=this_user,
                           applied=applied, 
                           shortlisted=shortlisted,
                           selected=selected,
                           rejected=rejected,
                           total_application=total_application,
                           drive=drive,
                           student=student,
                           company=company
                           )



@app.route("/admin/blacklist/<int:user_id>")
def blacklist_user(user_id) :
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    drive = PlacementDrive.query.filter_by(company_id=user_id).all()  #to get all the drives created by the company
    if user and user.role in ['student', 'company'] :
        user.is_active = False
        for d in drive :
            d.status = "closed"
        db.session.commit()
    return redirect(url_for('admin'))



@app.route("/admin/whitelist/<int:user_id>")
def whitelist_user(user_id) :
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if user and user.role in ['student', 'company'] :
        user.is_active = True
        db.session.commit()
    return redirect(url_for('admin'))



@app.route("/admin/approve-company/<int:user_id>")
def approve_company(user_id) :
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    company_id = User.query.get(user_id)

    # Ensure the user exists and is a company
    if company_id and company_id.role == 'company':
        company_id.is_approved = True
        db.session.commit()
    return redirect(url_for('admin'))



@app.route("/admin/reject-company/<int:user_id>")
def reject_company(user_id) :
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    company_id = User.query.get(user_id)

    if company_id and company_id.role == 'company' and not company_id.is_approved :
        db.session.delete(company_id)
        db.session.commit()
    return redirect(url_for('admin'))



@app.route("/admin/drive/<int:drive_id>")
def ad_view_drive_details(drive_id) :
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    this_user = User.query.get(session['user_id'])
    drive = PlacementDrive.query.get(drive_id)
    
    return render_template("admins_drive_details.html", this_user=this_user ,drive=drive)



@app.route("/admin/complete-drive/<int:drive_id>")
def ad_complete_drive(drive_id) :
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    drive = PlacementDrive.query.get(drive_id)

    if drive :
        drive.status = "closed"
        db.session.commit()
    return redirect(url_for('admin'))



@app.route("/admin/application/<int:app_id>")
def ad_view_Std_app(app_id) :
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    std_app = Application.query.get(app_id)

    return render_template("admins_std_application.html", std_app=std_app)



@app.route("/admin/application/status/<int:app_id>/<int:drive_id>")
def ad_std_status(app_id, drive_id) :
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        
        this_user = User.query.get(session['user_id'])
        drive = PlacementDrive.query.get(drive_id)
        application = Application.query.get(app_id)        

        return render_template("admins_app_status.html", this_user=this_user, drive=drive, application=application)





#################### ROUTES FOR COMPANY ####################################################################################



@app.route("/company")
def company() :
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))

    this_user = User.query.get(session['user_id'])
    upcoming_drives = PlacementDrive.query.filter_by(company_id=this_user.id, status='upcoming').all()        #to get all the upcoming drives created by the company
    closed_drives = PlacementDrive.query.filter_by(company_id=this_user.id, status='closed').all()            #to get all the closed drives created by the company
    application = Application.query.filter_by(id=this_user.id, status='applied').all()

    return render_template("company_dash.html", this_user=this_user, upcoming_drives=upcoming_drives, closed_drives=closed_drives, application=application)



@app.route("/company/edit", methods=['GET', 'POST'])
def cmp_edit_profile() :
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))

    company = User.query.get(session['user_id'])

    if request.method == 'POST' :
        name = request.form.get('name')
        website = request.form.get('website')
        hr = request.form.get('hr')
        headquarter = request.form.get('headquarter')
        brief = request.form.get('brief')

        company.username = name
        company.website = website
        company.hr_contact = hr
        company.headquarter = headquarter
        company.brief = brief
        db.session.commit()
        return redirect(url_for('company'))
    
    return render_template("company_edit_profile.html", company=company)



@app.route("/company/history/")
def cmp_history() :
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))

    company = User.query.get(session['user_id']) 
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    
    applications = []
    for drive in drives :
        applications.extend(drive.applications)

    return render_template("company_history.html", company=company,drives=drives, applications=applications)



@app.route("/company/create", methods=['GET', 'POST'])
def create_drive() :
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))

    company = User.query.get(session['user_id'])

    if request.method == 'POST' :
        company_id = session.get('user_id')
        name = request.form.get('name')
        title = request.form.get('title')
        desc = request.form.get('desc')
        loc = request.form.get('loc')
        elig = request.form.get('elig')
        sal = request.form.get('sal')
        deadline_str = request.form.get('deadline')
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()   #to convert the string input to a date object

        new_drive = PlacementDrive(
            company_id=company_id,
            name=name,
            job_title=title,
            job_description=desc,
            job_location=loc,
            eligibility_criteria=elig,
            job_salary=sal,
            application_deadline=deadline,
            status='upcoming')
        
        db.session.add(new_drive)
        db.session.commit()
        return redirect(url_for('company'))
    return render_template("company_create_drive.html", company=company)



@app.route("/company/update/<int:drive_id>", methods=['GET', 'POST'])
def update_drive(drive_id) :
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))
    
    company = User.query.get(session['user_id'])
    drive = PlacementDrive.query.get(drive_id)
    
    if request.method == 'POST' :
        desc =request.form.get('desc')
        loc = request.form.get('loc')
        elig = request.form.get('elig')
        sal = request.form.get('sal')
        deadline_str = request.form.get('deadline')
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()   

        drive.job_description = desc
        drive.job_location = loc
        drive.eligibility_criteria = elig
        drive.job_salary = sal
        drive.application_deadline = deadline
        drive.status = 'upcoming'   
        db.session.commit()
        return redirect(url_for('company'))
    return render_template("company_update_drive.html",company=company, drive=drive)



@app.route("/company/drive/<int:drive_id>")
def cmp_view_drive_details(drive_id) :
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))
    
    company = User.query.get(session['user_id'])
    student = User.query.get(session['user_id'])
    drive = PlacementDrive.query.get(drive_id)
    application = Application.query.filter_by(drive_id=drive_id).all() 

    return render_template("company_received_application.html", company=company, student=student, drive=drive, application=application)



@app.route("/company/complete-drive/<int:drive_id>")
def cmp_complete_drive(drive_id) :
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect(url_for('login'))

    drive = PlacementDrive.query.get(drive_id)

    if drive :
        drive.status = "closed"
        db.session.commit()
    return redirect(url_for('company'))



@app.route("/company/applications/<int:drive_id>")
def all_applications(drive_id) :
        if 'user_id' not in session or session.get('role') != 'company':
            return redirect(url_for('login'))
        
        company = User.query.get(session['user_id'])
        drive = PlacementDrive.query.get(drive_id)
        application = Application.query.filter_by(drive_id=drive_id).all()
        
        return render_template("company_received_application.html", company=company, drive=drive, application=application)   



@app.route("/company/applications/review/<int:app_id>/<int:drive_id>", methods=['GET', 'POST'])
def review(app_id, drive_id) :
        if 'user_id' not in session or session.get('role') != 'company':
            return redirect(url_for('login'))
        
        company = User.query.get(session['user_id'])
        drive = PlacementDrive.query.get(drive_id)
        application = Application.query.get(app_id)

        if request.method == 'POST' :
            status = request.form.get('status') 
            application.status = status
            application.remarks = request.form.get('remarks')
            application.application_date = datetime.now().date()
            db.session.commit()
            return redirect(url_for('all_applications', drive_id=application.drive_id))

        return render_template("companys_std_application.html", company=company, drive=drive, application=application)





#################### ROUTES FOR STUDENT ####################################################################################



@app.route("/student")
def student() :
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    this_user = User.query.get(session['user_id'])
    organizations = PlacementDrive.query.filter_by(status='upcoming').all()           # to get all the companies, whose drives are upcoming
    application = Application.query.filter_by(student_id=this_user.id).all()          #to get all the drives in which student has applied
    
    return render_template("std_dash.html", this_user=this_user, organizations=organizations, application=application)



@app.route("/student/edit", methods=['GET', 'POST'])
def std_edit_profile() :
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    student = User.query.get(session['user_id'])    

    if request.method == 'POST' :
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        dept = request.form.get('dept')
        cgpa = request.form.get('cgpa')

        student.username = name
        student.age = age
        student.gender = gender
        student.department = dept
        student.cgpa = cgpa
        db.session.commit()
        return redirect(url_for('student'))
    
    return render_template("std_edit_profile.html", student=student)



@app.route("/student/history/")
def std_history() :
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    student = User.query.get(session['user_id']) 
    application = Application.query.filter_by(student_id=student.id).all()  

    return render_template("std_history.html", student=student, application=application)



@app.route("/student/drive/<int:drive_id>")
def std_view_drive_details(drive_id) :
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    this_user = User.query.get(session['user_id'])
    drive = PlacementDrive.query.get(drive_id)    

    return render_template("std_drive_details.html", this_user=this_user, drive=drive)



@app.route("/student/apply/<int:drive_id>", methods=['GET', 'POST'])
def apply(drive_id) :

    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    student = User.query.get(session['user_id']) 
    drive = PlacementDrive.query.get(drive_id)
    application = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()  #to check if the student has already applied for the drive

    if application :
        return render_template("already_applied.html", student=student, drive=drive, application=application)

    if request.method == 'POST' :
        resume = request.form.get('resume')
        student.resume = resume
         
        new_application = Application(
            student_id=student.id,
            drive_id=drive_id,
            application_date=datetime.now().date()
        )
        db.session.add(new_application)
        db.session.commit()
        return redirect(url_for('student'))
    
    return render_template("std_apply.html", student=student, drive=drive, application=application)



@app.route("/student/status/<int:app_id>/<int:drive_id>")
def std_status(app_id, drive_id) :
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        
        this_user= User.query.get(session['user_id'])
        drive = PlacementDrive.query.get(drive_id)
        application = Application.query.get(app_id)        

        return render_template("std_app_status.html", this_user=this_user, drive=drive, application=application)

# 1. from models import * -> will look for this in the root directory
# 2. from .models import * -> will look for this in the current directory
# 3. from application.models import * -> controllers.py will think that there is one more application 