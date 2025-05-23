from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import User, Attempt

bp = Blueprint('profile', __name__)

@bp.route('/profile/<username>')
@login_required
def profile(username):
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
    
    return render_template('profile.html',
                         user=user,
                         attempts=attempts,
                         sent_boulders=sent_boulders,
                         flashes=flashes)

# You can add profile routes here later 