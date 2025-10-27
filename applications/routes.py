from main import app
from flask import render_template, session, url_for, redirect, request, flash
from applications.model import *
from datetime import datetime

# Helper Function
def is_admin():
    return session.get('username') == 'Admin' and session.get('role') == 'admin'

def is_professional():
    return session.get('role') == 'professional'

def is_customer():
    return session.get('role') == 'customer'

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check Admin Login
        if email == 'admin@example.com' and password == 'admin_password':  # Replace with hashed check if necessary
            session['username'] = 'Admin'
            session['role'] = 'admin'
            flash('Welcome, Admin!', 'success')
            return redirect(url_for('admin_dashboard'))

        # Regular User Login
        user = User.query.filter_by(email=email).first()
        if not user or user.password != password:  # If password is hashed, use check_password_hash
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

        # Set session and redirect based on role
        session['username'] = user.username
        session['role'] = [role.name for role in user.roles][0]
        session['user_id'] = user.id

        if session['role'] == 'customer':
            return redirect(url_for('customer_dashboard'))
        elif session['role'] == 'professional':
            return redirect(url_for('professional_dashboard'))
    return render_template('login.html')


# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear the entire session
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_name = request.form.get('role')

        # Validate unique username and email
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('login'))

        # Assign the role
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('signup'))

        # Create and store the user
        approved = role_name != 'professional'  # Only professionals require admin approval
        new_user = User(username=username, email=email, password=password, roles=[role], approved=approved)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


# Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    # Metrics
    total_customers = User.query.filter(User.roles.any(name='customer')).count()
    total_professionals = User.query.filter(User.roles.any(name='professional')).count()
    total_services = Services.query.count()
    total_earnings = sum(booking.cost for booking in Booking.query.filter_by(status='completed').all())

    # Pending approvals
    pending_approvals = User.query.filter_by(approved=False).filter(User.roles.any(name='professional')).all()

    # All service bookings
    all_bookings = Booking.query.all()

    return render_template(
        'admin_dashboard.html',
        total_customers=total_customers,
        total_professionals=total_professionals,
        total_services=total_services,
        total_earnings=total_earnings,
        pending_approvals=pending_approvals,
        all_bookings=all_bookings
    )


# Professional Dashboard
@app.route('/professional/dashboard')
def professional_dashboard():
    if not is_professional():
        flash('Access denied. Professionals only.', 'danger')
        return redirect(url_for('login'))

    professional_id = session.get('user_id')

    # Query pending, accepted, and completed bookings for this professional
    pending_requests = Booking.query.filter_by(status='pending').all()
    accepted_bookings = Booking.query.filter_by(status='accepted', professional_id=professional_id).all()
    completed_bookings = Booking.query.filter_by(status='completed', professional_id=professional_id).all()

    return render_template('professional_dashboard.html', 
                           pending_requests=pending_requests, 
                           accepted_bookings=accepted_bookings, 
                           completed_bookings=completed_bookings)

# Customer Dashboard
@app.route('/customer/dashboard')
def customer_dashboard():
    if not is_customer():
        flash('Access denied. Customers only.', 'danger')
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    # Fetch active bookings (pending or accepted)
    active_bookings = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.status.in_(['pending', 'accepted'])
    ).all()

    # Fetch completed bookings
    completed_bookings = Booking.query.filter_by(user_id=user_id, status='completed').all()

    return render_template(
        'customer_dashboard.html',
        active_bookings=active_bookings,
        completed_bookings=completed_bookings
    )



# User Approvals (Admin)
@app.route('/admin/user_approvals')
def user_approvals():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    pending_professionals = User.query.filter(User.roles.any(name='professional'), User.approved == False).all()
    return render_template('user_approvals.html', pending_professionals=pending_professionals)

@app.route('/admin/approve_user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    user.approved = True
    db.session.commit()
    flash(f'User {user.username} approved.', 'success')
    return redirect(url_for('user_approvals'))


@app.route('/admin/reject_user/<int:user_id>', methods=['POST'])
def reject_user(user_id):
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'{user.username} rejected successfully.', 'success')
    return redirect(url_for('user_approvals'))



@app.route('/admin/users')
def admin_users():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    # Fetch all users from the database
    users = User.query.all()
    return render_template('admin_users.html', users=users)

#permissions for loggin in with correct credintials
@app.route('/admin/permissions')
def permissions():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))
    return render_template('permissions.html')

@app.route('/customer/reports')
def customer_reports():
    if not is_customer():
        flash('Access denied. Customers only.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    completed_services = Booking.query.filter_by(user_id=user_id, status='completed').all()

    total_spending = sum(booking.cost for booking in completed_services)
    total_services = len(completed_services)

    return render_template('customer_reports.html',
                           total_spending=total_spending,
                           total_services=total_services,
                           completed_services=completed_services)



@app.route('/professional/reports')
def professional_reports():
    if not is_professional():
        flash('Access denied. Professionals only.', 'danger')
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    # Fetch completed services assigned to this professional
    completed_services = Booking.query.filter_by(professional_id=user_id, status='completed').all()

    # Calculate totals
    total_earnings = sum(booking.cost for booking in completed_services)
    total_services = len(completed_services)

    return render_template(
        'professional_reports.html',
        total_earnings=total_earnings,
        total_services=total_services,
        completed_services=completed_services
    )


@app.route('/admin/reports')
def admin_reports():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    # Fetch data
    total_customers = User.query.filter(User.roles.any(name='customer')).count()
    total_professionals = User.query.filter(User.roles.any(name='professional')).count()
    total_completed_services = Booking.query.filter_by(status='completed').count()
    total_earnings = sum(booking.cost for booking in Booking.query.filter_by(status='completed').all())
    completed_bookings = Booking.query.filter_by(status='completed').all()
    reviews = Review.query.all()  # Fetch all reviews

    return render_template(
        'admin_reports.html',
        total_customers=total_customers,
        total_professionals=total_professionals,
        total_completed_services=total_completed_services,
        total_earnings=total_earnings,
        completed_bookings=completed_bookings,
        reviews=reviews
    )


#search bar 
@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('search', None)

    if not search_query:
        flash('Please enter a search term.', 'danger')
        return redirect(url_for('home'))

    # Example: Filter services by name
    services = Services.query.filter(Services.service_name.ilike(f"%{search_query}%")).all()

    return render_template('search_results.html', search_query=search_query, services=services)


@app.route('/customer/book_service', methods=['GET', 'POST'])
def book_service():
    if not is_customer():
        flash('Access denied. Customers only.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session.get('user_id')
        service_id = request.form.get('service_id')
        date_requested = request.form.get('date_requested')  # Fetch the date input
        remarks = request.form.get('remarks', '')

        # Validate that date_requested is provided
        if not date_requested:
            flash('Please provide a valid date and time.', 'danger')
            return redirect(url_for('book_service'))

        try:
            # Parse the date_requested into a datetime object
            date_requested = datetime.strptime(date_requested, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format. Please use the datetime picker.', 'danger')
            return redirect(url_for('book_service'))

        # Fetch the service cost
        service = Services.query.get(service_id)
        if not service:
            flash('Invalid service selected.', 'danger')
            return redirect(url_for('book_service'))

        # Create the new booking
        new_booking = Booking(
            user_id=user_id,
            service_id=service_id,
            status='pending',
            remarks=remarks,
            date_requested=date_requested,
            cost=service.price  # Set the cost from the service
        )
        db.session.add(new_booking)
        db.session.commit()

        flash('Service booked successfully!', 'success')
        return redirect(url_for('customer_dashboard'))

    # Fetch all services to populate the dropdown
    services = Services.query.all()
    return render_template('book_service.html', services=services)



@app.route('/professional/requests', methods=['GET'])
def professional_requests():
    if not is_professional():
        flash('Access denied. Professionals only.', 'danger')
        return redirect(url_for('login'))

    pending_requests = Booking.query.filter_by(status='pending').all()
    return render_template('professional_requests.html', pending_requests=pending_requests)


@app.route('/professional/complete_booking/<int:booking_id>', methods=['POST'])
def complete_booking(booking_id):
    if not is_professional():
        flash('Access denied. Professionals only.', 'danger')
        return redirect(url_for('login'))

    booking = Booking.query.get(booking_id)
    if booking and booking.status == 'accepted':
        booking.status = 'completed'
        booking.date_completed = datetime.now()  # Update the completion date
        booking.remarks = request.form.get('remarks')  # Get remarks from the form
        db.session.commit()
        flash('Booking marked as completed.', 'success')
    else:
        flash('Invalid booking.', 'danger')
    return redirect(url_for('professional_dashboard'))


@app.route('/admin/bookings')
def admin_bookings():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    bookings = Booking.query.all()
    return render_template('admin_bookings.html', bookings=bookings)



@app.route('/customer/edit_request/<int:booking_id>', methods=['GET', 'POST'])
def edit_request(booking_id):
    if not session.get('role') == 'customer':
        flash('Access denied. Customers only.', 'danger')
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)

    if request.method == 'POST':
        booking.date_requested = request.form.get('date_requested')
        booking.remarks = request.form.get('remarks')
        db.session.commit()
        flash('Service request updated successfully!', 'success')
        return redirect(url_for('customer_dashboard'))

    return render_template('edit_request.html', booking=booking)


@app.route('/customer/close_request/<int:booking_id>', methods=['POST'])
def close_request(booking_id):
    if not session.get('role') == 'customer':
        flash('Access denied. Customers only.', 'danger')
        return redirect(url_for('login'))

    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'completed'
    db.session.commit()
    flash('Service request closed successfully!', 'success')
    return redirect(url_for('customer_dashboard'))

@app.route('/customer/search_services', methods=['GET', 'POST'])
def search_services():
    if not is_customer():
        flash('Access denied. Customers only.', 'danger')
        return redirect(url_for('login'))

    query = request.form.get('query', '').strip()
    services = Services.query.filter(Services.service_name.ilike(f'%{query}%')).all() if query else []
    if not services:
        flash('No services found matching your query.', 'info')

    return render_template('search_services.html', services=services, query=query)


@app.route('/admin/search_professionals', methods=['GET', 'POST'])
def search_professionals():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    professionals = []
    if request.method == 'POST':
        query = request.form.get('query')
        professionals = User.query.filter(
            User.roles.any(name='professional'),
            (User.username.ilike(f'%{query}%')) | (User.email.ilike(f'%{query}%'))
        ).all()

    return render_template('admin_search_professionals.html', professionals=professionals)


@app.route('/admin/search_bookings', methods=['GET', 'POST'])
def search_bookings():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    bookings = []
    if request.method == 'POST':
        query = request.form.get('query')
        bookings = Booking.query.join(User, Booking.user_id == User.id).join(
            Services, Booking.service_id == Services.id
        ).filter(
            (User.username.ilike(f'%{query}%')) | 
            (Services.service_name.ilike(f'%{query}%')) | 
            (User.email.ilike(f'%{query}%'))
        ).all()

    return render_template('admin_search_bookings.html', bookings=bookings)


@app.route('/admin/update_booking/<int:booking_id>', methods=['POST'])
def update_booking(booking_id):
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    booking = Booking.query.get_or_404(booking_id)
    action = request.form.get('action')

    if action == 'complete':
        booking.status = 'completed'
        booking.date_completed = datetime.now()
    elif action == 'cancel':
        booking.status = 'cancelled'

    db.session.commit()
    flash('Booking status updated successfully!', 'success')
    return redirect(url_for('admin_bookings'))



@app.route('/professional/view_requests', methods=['GET'])
def view_requests():
    if not is_professional():
        flash('Access denied. Professionals only.', 'danger')
        return redirect(url_for('login'))

    requests = Booking.query.filter_by(status='pending').all()
    return render_template('professional_requests.html', requests=requests)

@app.route('/customer/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if not is_customer():
        flash('Access denied. Customers only.', 'danger')
        return redirect(url_for('login'))

    booking = Booking.query.get_or_404(booking_id)

    if booking.status not in ['pending', 'accepted']:
        flash('You can only cancel pending or accepted bookings.', 'danger')
        return redirect(url_for('customer_dashboard'))

    db.session.delete(booking)
    db.session.commit()

    flash('Booking canceled successfully.', 'success')
    return redirect(url_for('customer_dashboard'))


@app.route('/professional/respond_request', methods=['POST'])
def professional_respond_request():
    if not is_professional():
        flash('Access denied. Professionals only.', 'danger')
        return redirect(url_for('login'))

    booking_id = request.form.get('booking_id')
    action = request.form.get('action')

    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Invalid booking request.', 'danger')
        return redirect(url_for('professional_requests'))

    if action == 'accept':
        booking.status = 'accepted'
        booking.professional_id = session.get('user_id')  # Assign the logged-in professional
        flash('Booking accepted.', 'success')
    elif action == 'reject':
        booking.status = 'rejected'
        flash('Booking rejected.', 'info')

    db.session.commit()
    return redirect(url_for('professional_requests'))

@app.route('/professional/accept_booking/<int:booking_id>', methods=['POST'])
def accept_booking(booking_id):
    if not is_professional():
        flash('Access denied. Professionals only.', 'danger')
        return redirect(url_for('login'))

    booking = Booking.query.get(booking_id)
    if booking and booking.status == 'pending':
        booking.status = 'accepted'
        booking.professional_id = session.get('user_id')  # Assign to logged-in professional
        db.session.commit()
        flash('Booking accepted successfully.', 'success')
    else:
        flash('Invalid booking.', 'danger')
    return redirect(url_for('professional_dashboard'))


@app.route('/professional/reject_booking/<int:booking_id>', methods=['POST'])
def reject_booking(booking_id):
    if not is_professional():
        flash('Access denied. Professionals only.', 'danger')
        return redirect(url_for('login'))

    booking = Booking.query.get(booking_id)
    if booking and booking.status == 'pending':
        booking.status = 'rejected'
        db.session.commit()
        flash('Booking rejected successfully.', 'success')
    else:
        flash('Invalid booking.', 'danger')
    return redirect(url_for('professional_dashboard'))


@app.route('/professional/search_requests', methods=['GET', 'POST'])
def search_requests():
    if not is_professional():
        flash('Access denied. Professionals only.', 'danger')
        return redirect(url_for('login'))

    requests = []
    if request.method == 'POST':
        query = request.form.get('query')
        requests = Booking.query.filter_by(professional_id=session.get('user_id')).join(
            Services, Booking.service_id == Services.id
        ).filter(
            (Services.service_name.ilike(f'%{query}%'))
        ).all()

    return render_template('professional_search_requests.html', requests=requests)


@app.route('/admin/manage_users', methods=['GET'])
def manage_users():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    # Fetch all users excluding admin
    users = User.query.filter(User.roles.any(name='customer') | User.roles.any(name='professional')).all()
    return render_template('admin_manage_users.html', users=users)


@app.route('/admin/remove_user/<int:user_id>', methods=['POST'])
def remove_user(user_id):
    if not is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_dashboard'))

    user = User.query.get_or_404(user_id)

    # Delete related bookings
    Booking.query.filter_by(user_id=user.id).delete()
    Booking.query.filter_by(professional_id=user.id).delete()

    # Delete related reviews
    Review.query.filter_by(professional_id=user.id).delete()

    # Finally, delete the user
    db.session.delete(user)
    db.session.commit()

    flash(f'User {user.username} and their associated data have been removed.', 'success')
    return redirect(url_for('manage_users'))



@app.route('/admin/add_service', methods=['GET', 'POST'])
def add_service():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        service_name = request.form.get('service_name')
        price = request.form.get('price')
        
        if not service_name or not price:
            flash('Service name and price are required.', 'danger')
            return redirect(url_for('add_service'))
        
        # Check if the service already exists
        existing_service = Services.query.filter_by(service_name=service_name).first()
        if existing_service:
            flash('Service already exists.', 'danger')
            return redirect(url_for('add_service'))
        
        # Add new service
        try:
            new_service = Services(service_name=service_name, price=int(price))
            db.session.add(new_service)
            db.session.commit()
            flash('Service added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding service: {e}', 'danger')
        
        return redirect(url_for('admin_services'))
    
    return render_template('add_service.html')


@app.route('/admin/services')
def admin_services():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))
    
    services = Services.query.all()
    return render_template('admin_services.html', services=services)


@app.route('/admin/remove_service/<int:service_id>', methods=['POST'])
def remove_service(service_id):
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))
    
    service = Services.query.get(service_id)
    if not service:
        flash('Service not found.', 'danger')
        return redirect(url_for('admin_services'))
    
    try:
        db.session.delete(service)
        db.session.commit()
        flash(f'Service "{service.service_name}" removed successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing service: {e}', 'danger')

    return redirect(url_for('admin_services'))


@app.route('/customer/review/<int:booking_id>', methods=['GET', 'POST'])
def leave_review(booking_id):
    if not is_customer():
        flash('Access denied. Customers only.', 'danger')
        return redirect(url_for('login'))

    booking = Booking.query.get_or_404(booking_id)

    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        feedback = request.form.get('feedback', '')

        # Create a new review
        new_review = Review(
            booking_id=booking.id,
            customer_id=booking.user_id,
            professional_id=booking.professional_id,
            service_id=booking.service_id,
            rating=rating,
            feedback=feedback
        )
        db.session.add(new_review)
        db.session.commit()

        flash('Review submitted successfully!', 'success')
        return redirect(url_for('customer_dashboard'))

    return render_template('leave_review.html', booking=booking)
