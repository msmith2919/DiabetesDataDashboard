# Diabetes Data Dashboard
from datetime import datetime

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://test:1234@CIT-SP-23\SQLEXPRESS/Nightscout?driver=ODBC+Driver+17+for+SQL+Server'
db = SQLAlchemy(app)

# BEGIN MONGO CODE

mongo_client = MongoClient("mongodb+srv://pythonuser:HHYoB8i8QZjT7G6U@diabetes-data.wvlkz0f.mongodb.net/test?retryWrites=true&w=majority")
mongo_db = mongo_client.test

# Add manual entry to MongoDB
@app.route('/addmanualentry', methods=['POST'])
def add_manual_entry():
    note_type = request.form['note_type']
    note_text = request.form['note_text']
    entry_time = datetime.now()
    manual_entry = {
        'note_type': note_type,
        'note_text': note_text,
        'entry_time': entry_time
    }
    mongo_db.manualentries.insert_one(manual_entry)
    return redirect('/')

@app.route('/manualentries')
def manual_entries():
    manual_entries = list(mongo_db.manualentries.find())
    return render_template('index.html', manual_entries=manual_entries)
# Delete a Manual Entry
@app.route('/delete_manual_entry/<entry_id>/delete', methods=['POST'])
def delete_manual_entry(entry_id):
    if request.method == 'POST':
        # convert the entry_id to ObjectId
        entry_id = ObjectId(entry_id)

        # delete the entry from the database
        mongo_db.manualentries.delete_one({'_id': entry_id})

    return redirect('/')

# END MANUAL ENTRY CODE FOR MONGODB

class User(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.String(50), primary_key=True)
    Name = db.Column(db.String(50))
    Email = db.Column(db.String(50))
    UserType = db.Column(db.String(50))
    Permissions = db.Column(db.String(50))
    Age = db.Column(db.Integer)
    Weight = db.Column(db.Integer)
    Height = db.Column(db.Integer)


class Device(db.Model):
    __tablename__ = 'Devices'
    DeviceID = db.Column(db.Integer, primary_key=True)
    DeviceName = db.Column(db.String(50))
    DeviceType = db.Column(db.String(50))
    UserID = db.Column(db.String(50), db.ForeignKey('Users.UserID'))

class TreatmentProfile(db.Model):
    __tablename__ = 'TreatmentProfiles'
    ProfileID = db.Column(db.Integer, primary_key=True)
    CarbRatio = db.Column(db.Float)
    ISF = db.Column(db.Float)
    BasalRate = db.Column(db.Float)
    TargetBG = db.Column(db.Float)
    UserID = db.Column(db.String(50), db.ForeignKey('Users.UserID'))
    CreateDate = db.Column(db.Date)

@app.route('/')
def index():
    users = User.query.all()
    devices = Device.query.all()
    treatment_profiles = TreatmentProfile.query.all()
    manual_entries = list(mongo_db.manualentries.find())
    return render_template('index.html', users=users, devices=devices, treatment_profiles=treatment_profiles, manual_entries=manual_entries)

@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        usertype = request.form['usertype']
        userpermissions = request.form['userpermissions']
        age = request.form['age']
        weight = request.form['weight']
        height = request.form['height']
        user = User(UserID=name, Name=name, Email=email, Age=age, UserType=usertype, Permissions=userpermissions, Weight=weight, Height=height)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('add.html')

@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.filter_by(UserID=id).first()
    if request.method == 'POST':
        user.Name = request.form['name']
        user.Email = request.form['email']
        user.UserType = request.form['usertype']
        user.Permissions = request.form['userpermissions']
        user.Age = request.form['age']
        user.Weight = request.form['weight']
        user.Height = request.form['height']
        db.session.commit()
        return redirect('/')
    return render_template('edit.html', user=user)

# Add Device
@app.route('/adddevice', methods=['GET', 'POST'])
def add_device():
    users = User.query.all()
    if request.method == 'POST':
        device_name = request.form['device_name']
        device_type = request.form['device_type']
        user_id = request.form['user_id']
        device = Device(DeviceName=device_name, DeviceType=device_type, UserID=user_id)
        db.session.add(device)
        db.session.commit()
        return redirect('/')
    return render_template('adddevice.html', users=users)

# Edit Device
@app.route('/editdevice/<int:device_id>', methods=['GET', 'POST'])
def edit_device(device_id):
    device = Device.query.filter_by(DeviceID=device_id).first()
    users = User.query.all()
    if request.method == 'POST':
        device.DeviceName = request.form['device_name']
        device.DeviceType = request.form['device_type']
        device.UserID = request.form['user_id']
        db.session.commit()
        return redirect('/')
    return render_template('editdevice.html', device=device, users=users)

# Delete Device
@app.route('/devices/<int:device_id>/delete', methods=['POST'])
def delete_device(device_id):
    if request.method == 'POST':
        device = Device.query.get_or_404(device_id)
        db.session.delete(device)
        db.session.commit()
        return redirect('/')
    else:
        return abort(405)  # Return "Method Not Allowed" error


# Delete User
@app.route('/delete/<string:id>')
def delete_user(id):
    user = User.query.filter_by(UserID=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect('/')

# Add Treatment Profile
@app.route('/addtreatment', methods=['GET', 'POST'])
def add_treatment_profile():
    users = User.query.all()
    if request.method == 'POST':
        carb_ratio = request.form['carb_ratio']
        isf = request.form['isf']
        basal_rate = request.form['basal_rate']
        target_bg = request.form['target_bg']
        user_id = request.form['user_id']
        create_date = datetime.now()
        treatment_profile = TreatmentProfile(
            CarbRatio=carb_ratio,
            ISF=isf,
            BasalRate=basal_rate,
            TargetBG=target_bg,
            UserID=user_id,
            CreateDate=create_date
        )
        db.session.add(treatment_profile)
        db.session.commit()
        return redirect('/')
    return render_template('addtreatment.html', users=users)

# Edit Treatment Profile
@app.route('/edittreatment/<int:treatment_id>', methods=['GET', 'POST'])
def edit_treatment_profile(treatment_id):
    treatment = db.session.query(TreatmentProfile).get(treatment_id)
    form = TreatmentProfileForm(obj=treatment)
    if form.validate_on_submit():
        form.populate_obj(treatment)
        db.session.commit()
        return redirect('/')
    return render_template('edittreatment.html', form=form, treatment=treatment)

#Delete Treatment Profile
@app.route('/delete_treatment_profile/<int:treatment_id>', methods=['POST'])
def delete_treatment_profile(treatment_id):
    treatment = TreatmentProfile.query.get_or_404(treatment_id)
    db.session.delete(treatment)
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)