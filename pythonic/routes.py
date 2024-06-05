from datetime import datetime , time, timedelta 
import secrets
import os
import logging
import requests
from venv import logger
from PIL import Image
from werkzeug.utils import secure_filename
from flask import  jsonify,abort, render_template, url_for, flash, redirect, request, session
from instance.helper import get_cleaning_users_from_database, get_electrical_users_from_database, get_plumbing_users_from_database,get_Carpentry_users_from_database,get_Painting_users_from_database,get_movingFur_users_from_database
from pythonic.forms import ProblemForm, RegistrationForm, LoginForm,NewWorkForm, UpdateProfileForm,AppointmentForm,NewLessonForm,AppointmentActionForm
from pythonic import app, bcrypt, db
from flask_login import login_required, login_user, current_user, logout_user
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pythonic.models import Appointment, Slot, User,Availability,Service,Work,Rating
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem.porter import PorterStemmer
from sqlalchemy import and_
from flask import current_app

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', 'uploads', picture_name)

    # Resize and save the image
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_name

@app.route("/")
@app.route("/index")
def home():
    return render_template('home.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            address=form.address.data,
            contactNumber=form.contactNumber.data,
            user_type=form.user_type.data,
        )
        if form.user_type.data == 'craft_owner':
            user.service_type = form.service_type.data
            user.description = form.description.data
        db.session.add(user)
        db.session.commit()
        login_user(user)

        flash(f"Account created successfully for {form.username.data} as a {form.user_type.data}", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)
 
@app.route("/aboutUs")
def about():
    return render_template('about.html')


@app.route("/services")
def services():
    services = Service.query.all()  # Fetch all services from the database
    return render_template('services.html', services=services)

@app.route('/service_work/<int:service_id>')
def service_work(service_id):
    # Retrieve work related to the selected service from the database
    service = Service.query.get_or_404(service_id)
    works = service.works
    return render_template('service_work.html', service=service, works=works)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("You have been logged in!", "success")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check credentials", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/get_slots')
@login_required
def get_slots():
    selected_date_str = request.args.get('date')
    craft_owner_name = request.args.get('craft_owner')

    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    user = User.query.filter_by(username=craft_owner_name).first()
    if not user:
        return jsonify({'error': 'Craft owner not found'}), 404

    availabilities = Availability.query.filter_by(owner_id=user.id).all()
    if not availabilities:
        return jsonify({'slots': []})

    availability_ids = [availability.id for availability in availabilities]
    slots = Slot.query.filter(
        Slot.availability_id.in_(availability_ids),
        Slot.is_available == True,
        Slot.date == selected_date
    ).all()

    slot_data = [{'period': slot.period} for slot in slots]
    return jsonify({'slots': slot_data})


@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    form = AppointmentForm()

    craft_owner_name = request.args.get('craft_owner') or form.craft_owner.data
    service_type = request.args.get('service_type') or form.service_type.data
    selected_date_str = request.args.get('appointment_date') or form.appointment_date.data

    app.logger.debug(f"Craft Owner: {craft_owner_name}")
    app.logger.debug(f"Service Type: {service_type}")
    app.logger.debug(f"Selected Date (str): {selected_date_str}")

    if isinstance(selected_date_str, str):
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = None
            app.logger.error(f"Invalid date format for selected_date: {selected_date_str}")
    else:
        selected_date = selected_date_str

    app.logger.debug(f"Converted selected_date to: {selected_date}")

    available_dates = []
    available_slots = []
    slots = []

    if craft_owner_name:
        user = User.query.filter_by(username=craft_owner_name).first()
        app.logger.debug(f"Fetched user: {user}")
        if user:
            availabilities = Availability.query.filter_by(owner_id=user.id).all()
            app.logger.debug(f"Fetched availabilities: {availabilities}")
            availability_ids = [availability.id for availability in availabilities]
            app.logger.debug(f"Collected availability_ids: {availability_ids}")
            available_slots = Slot.query.filter(Slot.availability_id.in_(availability_ids)).all()
            app.logger.debug(f"Fetched available slots: {available_slots}")
            available_dates = sorted(set([slot.date for slot in available_slots]))
            app.logger.debug(f"Extracted available dates: {available_dates}")

            if selected_date:
                slots = Slot.query.filter(
                    Slot.availability_id.in_(availability_ids),
                    Slot.is_available == True,
                    Slot.date == selected_date
                ).all()
                app.logger.debug(f"Filtered slots query: {slots}")
            else:
                app.logger.debug("Selected date is None or invalid.")

    if request.method == 'POST' :
        app.logger.debug("Form validated successfully")
        selected_slot = Slot.query.filter_by(
            period=form.appointment_time.data,
            date=form.appointment_date.data,
            is_available=True
        ).first()

        if selected_slot:
            try:
                app.logger.debug(f"Selected slot: {selected_slot}")
                
                # Convert form.appointment_date.data to date object
                appointment_date = datetime.strptime(form.appointment_date.data, '%Y-%m-%d').date()

                appointment = Appointment(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    phone_number=form.phone_number.data,
                    street_address=form.street_address.data,
                    city=form.city.data,
                    state=form.state.data,
                    postal_code=form.postal_code.data,
                    appointment_date=appointment_date,
                    appointment_time=form.appointment_time.data,
                    craft_owner=craft_owner_name,
                    customer_id=current_user.id,
                    appointment_purpose=form.appointment_purpose.data,
                    message=form.message.data
                )
                app.logger.debug(f"Appointment object created: {appointment}")
                db.session.add(appointment)
                selected_slot.is_available = False
                db.session.commit()
                app.logger.debug("Appointment committed to the database and slot availability updated")
                flash('Your appointment has been booked!', 'success')
                return redirect(url_for('home'))
            except Exception as e:
                app.logger.error(f"An error occurred while committing to the database: {str(e)}")
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'danger')
        else:
            flash('The selected slot is no longer available. Please choose another slot.', 'danger')

    form.craft_owner.data = craft_owner_name
    form.service_type.data = service_type

    return render_template('appointments.html', form=form, craft_owner=craft_owner_name, service_type=service_type, available_dates=available_dates, slots=slots)

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        title="Dashboard",
        active_tab=None
    )

@app.route('/dashboard/myWorks', methods=['GET'])
@login_required
def myWorks():
    works = Work.query.filter_by(user_id=current_user.id).all()
    return render_template('myWorks.html', works=works)

@app.route('/dashboard/edit_work/<int:work_id>', methods=['GET', 'POST'])
@login_required
def edit_work(work_id):
    work = Work.query.get_or_404(work_id)
    if work.user_id != current_user.id:
        abort(403)
    form = NewWorkForm()
    if form.validate_on_submit():
        work.title = form.title.data
        work.content = form.content.data
        if form.images.data:
            for f in form.images.data:
                filename = secure_filename(f.filename)
                filepath = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
                f.save(filepath)
                work.img = filename
        db.session.commit()
        flash('Your work has been updated!', 'success')
        return redirect(url_for('myWorks'))
    elif request.method == 'GET':
        form.title.data = work.title
        form.content.data = work.content
    return render_template('edit_work.html', form=form, work=work)


@app.route('/dashboard/delete_work/<int:work_id>', methods=['POST', 'DELETE'])
def delete_work(work_id):
    work = Work.query.get_or_404(work_id)
    # Add check if current user is allowed to delete this work
    db.session.delete(work)
    db.session.commit()
    flash('Work deleted successfully', 'success')
    return redirect(url_for('myWorks'))

@app.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    image_file = url_for('static', filename=f'user_pics/{user.image_file}')
    is_current_user = (user.id == current_user.id)
    profile_form = UpdateProfileForm(obj=user) if is_current_user else None
    return render_template(
        'profile.html',
        title=f"{user.username}'s Profile",
        user=user,
        image_file=image_file,
        active_tab='profile',
        is_current_user=is_current_user,
        profile_form=profile_form
    )


@app.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    profile_form = UpdateProfileForm()
    if profile_form.validate_on_submit():
        if profile_form.picture.data:
            picture_file = save_picture(profile_form.picture.data)
            current_user.image_file = picture_file
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.address = profile_form.address.data
        current_user.contactNumber = profile_form.contactNumber.data
        current_user.description = profile_form.description.data
        db.session.commit()
        flash('Your profile has been updated', 'success')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email
        profile_form.address.data = current_user.address
        profile_form.contactNumber.data = current_user.contactNumber
        profile_form.description.data = current_user.description
    image_file = url_for('static', filename=f'user_pics/{current_user.image_file}')
    return render_template(
        'profile.html',
        title='Profile',
        profile_form=profile_form,
        image_file=image_file,
        active_tab='profile',
        is_current_user=True
    )

@app.route("/dashboard/new_lesson", methods=["GET", "POST"])
@login_required
def new_lesson():
    new_lesson_form = NewLessonForm()

    if new_lesson_form.validate_on_submit():
        # Extract data from the form
        start_time = new_lesson_form.start_time.data
        end_time = new_lesson_form.end_time.data
        all_days = new_lesson_form.all_days.data

        # If "Work All Days" checkbox is selected, set working_days to all days of the week
        if all_days:
            working_days = "sunday,monday,tuesday,wednesday,thursday,friday,saturday"
        else:
            working_days = ','.join(new_lesson_form.workingDays.data)

        # Remove any accidental extra commas and spaces
        working_days = ','.join([day.strip() for day in working_days.split(',') if day.strip()])

        # Create a new Availability object
        availability = Availability(
            start_time=start_time,
            end_time=end_time,
            days=working_days,
            owner_id=current_user.id  # Associate with the current user
        )

        # Add the availability to the database session
        db.session.add(availability)
        db.session.commit()

        # Generate slots
        working_days_list = working_days.split(',')

        # Assuming you want to generate slots for a period of one month
        start_date = datetime.today()
        end_date = start_date + timedelta(days=30)

        current_date = start_date
        while current_date <= end_date:
            day_name = current_date.strftime('%A').lower()
            if day_name in working_days_list:
                # Generate slots for this date
                current_time = datetime.combine(current_date, start_time)
                end_time_today = datetime.combine(current_date, end_time)
                slot_duration = timedelta(minutes=60)

                while current_time + slot_duration <= end_time_today:
                    period = f"{current_time.time()}-{(current_time + slot_duration).time()}"
                    slot = Slot(
                        period=period,
                        duration=60,
                        availability_id=availability.id,
                        is_available=1,  # Assuming new slots are available by default
                        date=current_date.date()
                    )
                    db.session.add(slot)
                    current_time += slot_duration
            current_date += timedelta(days=1)

        db.session.commit()

        flash("Your availability has been updated!", "success")
        return redirect(url_for("dashboard"))  # Redirect to dashboard page after submission

    # If the form is not submitted or validation fails, render the new_lesson.html template
    return render_template(
        "new_lesson.html",
        title="New Lesson",
        new_lesson_form=new_lesson_form,
        active_tab="new_lesson"
    )

@app.route("/dashboard/manage_appointments", methods=["GET", "POST"])
@login_required
def manage_appointments():
    craft_owner_username = current_user.username
    pending_appointments = Appointment.query.filter_by(craft_owner=craft_owner_username, status='Pending').all()
    scheduled_appointments = Appointment.query.filter_by(craft_owner=craft_owner_username, status='Scheduled').all()
    in_progress_appointments = Appointment.query.filter_by(craft_owner=craft_owner_username, status='In Progress').all()
    done_appointments = Appointment.query.filter_by(craft_owner=craft_owner_username, status='Done').all()
    
    form = AppointmentActionForm()

    if form.validate_on_submit():
        appointment_id = request.form.get('appointment_id')
        action = request.form.get('action')
        expected_budget = request.form.get('expected_budget')  # Get the expected budget from the form
        appointment = Appointment.query.get(appointment_id)

        if appointment and appointment.craft_owner == craft_owner_username:
            if expected_budget:
                appointment.expected_budget = expected_budget  # Save the expected budget to the appointment
            if action == 'schedule':
                appointment.status = 'Scheduled'
                flash('Appointment scheduled.', 'success')
            elif action == 'in_progress':
                appointment.status = 'In Progress'
                flash('Appointment is now in progress.', 'success')
            elif action == 'done':
                appointment.status = 'Done'
                flash('Appointment is marked as done.', 'success')
            db.session.commit()
        else:
            flash('Invalid appointment action.', 'danger')
        return redirect(url_for('manage_appointments'))

    return render_template('manage_appointments.html', 
                        pending_appointments=pending_appointments, 
                        scheduled_appointments=scheduled_appointments, 
                        in_progress_appointments=in_progress_appointments, 
                        done_appointments=done_appointments, 
                        form=form)



@app.route("/dashboard/customerAppointments", methods=["GET", "POST"])
@login_required
def customer_appointments():
    customer_id = current_user.id  # Assuming customer ID is stored in the user session

    pending_appointments = Appointment.query.filter_by(customer_id=customer_id, status='Pending').all()
    scheduled_appointments = Appointment.query.filter_by(customer_id=customer_id, status='Scheduled').all()
    in_progress_appointments = Appointment.query.filter_by(customer_id=customer_id, status='In Progress').all()
    done_appointments = Appointment.query.filter_by(customer_id=customer_id, status='Done').all()
    canceled_appointments = Appointment.query.filter_by(customer_id=customer_id, status='Canceled').all()

    print(f"Pending Appointments: {pending_appointments}")
    print(f"Scheduled Appointments: {scheduled_appointments}")
    print(f"In Progress Appointments: {in_progress_appointments}")
    print(f"Done Appointments: {done_appointments}")
    print(f"Canceled Appointments: {canceled_appointments}")

    return render_template('customerAppointments.html',
                        pending_appointments=pending_appointments,
                        scheduled_appointments=scheduled_appointments,
                        in_progress_appointments=in_progress_appointments,
                        done_appointments=done_appointments,
                        canceled_appointments=canceled_appointments)

@app.route("/cancel_appointment/<int:appointment_id>", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.customer_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized access"}), 403
    
    appointment.status = 'Canceled'
    db.session.commit()
    return jsonify({"success": True})

@app.route("/dashboard/newWork", methods=["GET", "POST"])
@login_required
def newWork():
    form = NewWorkForm()
    if form.validate_on_submit():
        files = []
        for f in form.images.data:
            filename = save_picture(f)  # Save the image using the save_picture function
            files.append(filename)

        # Save the work details to the database
        work = Work(
            title=form.title.data,
            content=form.content.data,
            img=files[0],
            user_id=current_user.id,
            service_id=current_user.service_id
        )
        db.session.add(work)
        db.session.commit()
        flash('Your work has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('newWork.html', form=form, craft_owner=current_user)



@app.route('/plumbing')
def plumbing():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    users, total_users, total_pages = get_plumbing_users_from_database(page, per_page)
    next_url = url_for('plumbing', page=page + 1) if page < total_pages else None
    prev_url = url_for('plumbing', page=page - 1) if page > 1 else None
    pages = range(1, total_pages + 1)
    return render_template('plumbing.html', plumbing_users=users, next_url=next_url, prev_url=prev_url, pages=pages, current_page=page)

@app.route('/electrical')
def electrical():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    users, total_users, total_pages = get_electrical_users_from_database(page, per_page)
    next_url = url_for('electrical', page=page + 1) if page < total_pages else None
    prev_url = url_for('electrical', page=page - 1) if page > 1 else None
    pages = range(1, total_pages + 1)
    return render_template('electrical.html', electrical_users=users, next_url=next_url, prev_url=prev_url, pages=pages, current_page=page)

@app.route('/cleaning')
def cleaning():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    users, total_users, total_pages = get_cleaning_users_from_database(page, per_page)
    next_url = url_for('cleaning', page=page + 1) if page < total_pages else None
    prev_url = url_for('cleaning', page=page - 1) if page > 1 else None
    pages = range(1, total_pages + 1)
    return render_template('cleaning.html', cleaning_users=users, next_url=next_url, prev_url=prev_url, pages=pages, current_page=page)

@app.route('/movingFur')
def movingFur():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    users, total_users, total_pages = get_movingFur_users_from_database(page, per_page)
    next_url = url_for('movingFur', page=page + 1) if page < total_pages else None
    prev_url = url_for('movingFur', page=page - 1) if page > 1 else None
    pages = range(1, total_pages + 1)
    return render_template('movingFur.html', movingFur_users=users, next_url=next_url, prev_url=prev_url, pages=pages, current_page=page)

@app.route('/Carpentry')
def Carpentry():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    users, total_users, total_pages = get_Carpentry_users_from_database(page, per_page)
    next_url = url_for('Carpentry', page=page + 1) if page < total_pages else None
    prev_url = url_for('Carpentry', page=page - 1) if page > 1 else None
    pages = range(1, total_pages + 1)
    return render_template('Carpentry.html', Carpentry_users=users, next_url=next_url, prev_url=prev_url, pages=pages, current_page=page)

@app.route('/Painting')
def Painting():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    users, total_users, total_pages = get_Painting_users_from_database(page, per_page)
    next_url = url_for('Painting', page=page + 1) if page < total_pages else None
    prev_url = url_for('Painting', page=page - 1) if page > 1 else None
    pages = range(1, total_pages + 1)
    return render_template('Painting.html', Painting_users=users, next_url=next_url, prev_url=prev_url, pages=pages, current_page=page)

@app.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    problem_form = ProblemForm()  # Instantiate the ProblemForm
    return render_template('booking.html', problem_form=problem_form)

@app.route('/handle_problem_form', methods=['POST'])
def handle_problem_form():
    problem_form = ProblemForm(request.form)
    if request.method == 'POST' and problem_form.validate():
        # Retrieve the problem description from the form data
        problem_description = problem_form.problem_description.data

        # Retrieve craft owners' names, descriptions, addresses, and service types from the User table in the database
        craft_owners = User.query.filter_by(user_type='Craft Owner').all()
        craft_owner_data = [(craft_owner.username, craft_owner.description, craft_owner.address, craft_owner.service_type) for craft_owner in craft_owners]

        # Recommend craft owners based on cosine similarity
        recommended_craft_owner_data = recommend_craft_owners(craft_owner_data, problem_description)

        # Render template with recommendation results
        return render_template('recommendation.html', problem_description=problem_description, recommended_craft_owner_data=recommended_craft_owner_data)
    
    # If form is not valid, render the form again
    return render_template('booking.html', problem_form=problem_form)


def preprocess_text(text):
    if text is None:
        return ""  # Return empty string if text is None
    
    # Tokenization, filtering, and lemmatization
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    preprocessed_tokens = []
    for word, tag in pos_tag(word_tokenize(text)):
        if word.casefold() not in stop_words and word.isalpha():
            pos = get_wordnet_pos(tag)
            if pos:
                preprocessed_tokens.append(lemmatizer.lemmatize(word, pos))
            else:
                preprocessed_tokens.append(lemmatizer.lemmatize(word))
    preprocessed_text = ' '.join(preprocessed_tokens)
    print("Preprocessed Text:", preprocessed_text)  # Debugging print statement
    return preprocessed_text


def get_wordnet_pos(tag):
    if tag.startswith("J"):
        return wordnet.ADJ
    elif tag.startswith("V"):
        return wordnet.VERB
    elif tag.startswith("N"):
        return wordnet.NOUN
    elif tag.startswith("R"):
        return wordnet.ADV
    else:
        return None

def recommend_craft_owners(craft_owner_data, customer_problem_description):
    # Preprocess craft owner descriptions and customer problem description
    preprocessed_craft_owner_descriptions = [preprocess_text(desc[1]) + " " + preprocess_text(desc[2]) for desc in craft_owner_data]
    preprocessed_customer_problem_description = preprocess_text(customer_problem_description)

    # Calculate TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(preprocessed_craft_owner_descriptions + [preprocessed_customer_problem_description])

    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1])

    # Get craft owners sorted by similarity score in descending order
    sorted_craft_owners = sorted(zip(craft_owner_data, similarity_matrix), key=lambda x: x[1], reverse=True)
    
    # Prepare craft owner data as a list of dictionaries
    recommended_craft_owner_data = []
    for craft_owner, similarity_score in sorted_craft_owners:
        name, description, address, service_type = craft_owner  # Ensure service_type is included here
        recommended_craft_owner_data.append({
            'name': name,
            'description': description,
            'address': address,
            'service_type': service_type,  # Include service_type
            'similarity_score': similarity_score[0]  # Assuming similarity_score is a single value in a list
        })

    return recommended_craft_owner_data

def update_average_ratings():
    craft_owners = User.query.filter_by(user_type='Craft Owner').all()
    
    for owner in craft_owners:
        ratings = Rating.query.filter_by(craft_owners(owner.id)).all()
        if ratings:
            avg_rating = sum(rating.rating for rating in ratings) / len(ratings)
            owner.average_rating = avg_rating
            db.session.commit()
        else:
            owner.average_rating = None
            db.session.commit()

@app.route('/update_average_ratings')
def update_average_ratings_route():
    update_average_ratings()
    return "Average ratings updated successfully."

@app.route('/rate_craft_owner', methods=['POST'])
def rate_craft_owner():
    data = request.json
    if not data:
        app.logger.error('No JSON data received')
        return jsonify({'success': False, 'error': 'No JSON data received'}), 400

    craft_owner_name = data.get('craft_owner')
    appointment_id = data.get('appointment_id')
    rating = data.get('rating')

    if not craft_owner_name or not appointment_id or not rating:
        app.logger.error(f'Invalid request data: {data}')
        return jsonify({'success': False, 'error': 'Invalid request data'}), 400

    user = User.query.filter_by(username=craft_owner_name, user_type='Craft Owner').first()
    appointment = Appointment.query.get(appointment_id)

    if not user or not appointment:
        app.logger.error(f'Craft owner or appointment not found: {craft_owner_name}, {appointment_id}')
        return jsonify({'success': False, 'error': 'Craft owner or appointment not found'}), 404

    new_rating = Rating(craft_owner_id=user.id, customer_id=appointment.customer_id, appointment_id=appointment.id, rating=rating)
    db.session.add(new_rating)
    db.session.commit()

    # Update average rating
    ratings = Rating.query.filter_by(craft_owner_id=user.id).all()
    avg_rating = sum(r.rating for r in ratings) / len(ratings)
    user.average_rating = avg_rating
    db.session.commit()

    app.logger.info(f'Successfully rated craft owner: {craft_owner_name} with rating {rating}')
    return jsonify({'success': True})

    
def translate_arabic_to_english(api_key, arabic_text):
    endpoint = "https://api.openai.com/v1/engines/davinci/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "prompt": arabic_text,
        "max_tokens": 100,
        "temperature": 0,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    response = requests.post(endpoint, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"]
    else:
        return None

@app.route('/transarb')
def transarb():
    return render_template('translate.html')

@app.route('/translate', methods=['POST'])
def translate():
    api_key = request.form['api_key']
    arabic_text = request.form['arabic_text']
    english_text = translate_arabic_to_english(api_key, arabic_text)
    return render_template('translate.html', english_text=english_text)
