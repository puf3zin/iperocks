from flask import Blueprint, render_template
from app.models import Sector, Block, Boulder

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    sectors = Sector.query.all()
    return render_template('public/index.html', sectors=sectors) 