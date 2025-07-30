"""
Admin panel routes
"""
from flask import render_template
from app.admin import admin_bp
from app.auth.decorators import admin_required


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')