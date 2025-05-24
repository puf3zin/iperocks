from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Sector, Block, Boulder, Tag, Attempt, User
from flask_login import current_user, login_required
from datetime import datetime
from app import db

bp = Blueprint('public', __name__)

@bp.route('/sector/<int:sector_id>')
def sector_detail(sector_id):
    sector = Sector.query.get_or_404(sector_id)
    blocks = Block.query.filter_by(sector_id=sector_id).all()
    return render_template('public/sector_detail.html', sector=sector, blocks=blocks)

@bp.route('/block/<int:block_id>')
def block_detail(block_id):
    block = Block.query.get_or_404(block_id)
    boulders = Boulder.query.filter_by(block_id=block_id).all()
    return render_template('public/block_detail.html', block=block, boulders=boulders)

@bp.route('/boulder/<int:boulder_id>')
def boulder_detail(boulder_id):
    boulder = Boulder.query.get_or_404(boulder_id)
    user_attempts = []
    all_attempts = Attempt.query.filter_by(boulder_id=boulder_id).order_by(Attempt.datetime.desc()).all()
    
    if current_user.is_authenticated:
        user_attempts = Attempt.query.filter_by(
            user_id=current_user.id,
            boulder_id=boulder_id
        ).order_by(Attempt.datetime.desc()).all()
    
    return render_template('public/boulder_detail.html', 
                         boulder=boulder,
                         user_attempts=user_attempts,
                         all_attempts=all_attempts)

@bp.route('/sectors')
def sectors():
    sectors = Sector.query.order_by(Sector.name).all()
    return render_template('public/sectors.html', sectors=sectors)

@bp.route('/boulders')
def boulders():
    boulders = Boulder.query.order_by(Boulder.grade).all()
    sectors = Sector.query.order_by(Sector.name).all()
    blocks = Block.query.order_by(Block.name).all()
    tags = Tag.query.order_by(Tag.name).all()
    
    # Get unique grades and sort them correctly
    def grade_sort_key(grade):
        if grade == 'P':
            return 18  # P is highest
        return int(grade[1:])  # Convert V0-V17 to numbers
    
    grades = sorted(list(set(b.grade for b in boulders)), key=grade_sort_key)
    
    return render_template('public/boulders.html', 
                         boulders=boulders,
                         sectors=sectors,
                         blocks=blocks,
                         tags=tags,
                         grades=grades)

@bp.route('/boulder/<int:boulder_id>/attempt', methods=['POST'])
@login_required
def log_attempt(boulder_id):
    boulder = Boulder.query.get_or_404(boulder_id)
    status = request.form.get('status')
    notes = request.form.get('notes', '')
    rating = request.form.get('rating')
    
    if status not in ['Tentativa', 'Cadena', 'Flash']:
        flash('Invalid attempt status', 'danger')
        return redirect(url_for('public.boulder_detail', boulder_id=boulder_id))
    
    attempt = Attempt(
        user_id=current_user.id,
        boulder_id=boulder.id,
        status=status,
        notes=notes,
        rating=rating
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    flash('Attempt logged successfully!', 'success')
    return redirect(url_for('public.boulder_detail', boulder_id=boulder_id))

@bp.route('/attempt/<int:attempt_id>/delete', methods=['POST'])
@login_required
def delete_attempt(attempt_id):
    attempt = Attempt.query.get_or_404(attempt_id)
    
    # Check if the attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash('You cannot delete this attempt.', 'danger')
        return redirect(url_for('public.boulder_detail', boulder_id=attempt.boulder_id))
    
    db.session.delete(attempt)
    db.session.commit()
    
    flash('Attempt deleted successfully!', 'success')
    return redirect(url_for('public.boulder_detail', boulder_id=attempt.boulder_id))

@bp.route('/users')
def users():
    users = User.query.order_by(User.username).all()
    return render_template('public/users.html', users=users)

@bp.route('/user/<username>')
def user_detail(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get all attempts
    all_attempts = Attempt.query.filter_by(user_id=user.id).order_by(Attempt.datetime.desc()).all()
    
    # Get sent boulders (Cadena or Flash)
    sent_boulders = Attempt.query.filter_by(
        user_id=user.id
    ).filter(
        Attempt.status.in_(['Cadena', 'Flash'])
    ).order_by(Attempt.datetime.desc()).all()
    
    # Get flashes
    flashes = Attempt.query.filter_by(
        user_id=user.id,
        status='Flash'
    ).order_by(Attempt.datetime.desc()).all()
    
    # Get only "Tentativa" attempts
    attempts = Attempt.query.filter_by(
        user_id=user.id,
        status='Tentativa'
    ).order_by(Attempt.datetime.desc()).all()
    
    return render_template('public/user_detail.html',
                         user=user,
                         attempts=attempts,
                         sent_boulders=sent_boulders,
                         flashes=flashes) 