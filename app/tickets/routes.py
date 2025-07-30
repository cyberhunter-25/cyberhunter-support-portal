"""
Ticket management routes
"""
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.tickets import tickets_bp
from app.auth.decorators import login_required


@tickets_bp.route('/')
@login_required
def index():
    """List user's tickets"""
    return render_template('tickets/index.html')


@tickets_bp.route('/create')
@login_required
def create():
    """Create new ticket"""
    return render_template('tickets/create.html')


@tickets_bp.route('/<int:ticket_id>')
@login_required
def view(ticket_id):
    """View ticket details"""
    return render_template('tickets/view.html', ticket_id=ticket_id)