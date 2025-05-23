from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Sector, Block, Boulder, Tag
import os
from werkzeug.utils import secure_filename
from flask import current_app
import pandas as pd

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/sector/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_sector():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        sector = Sector(name=name, description=description)
        db.session.add(sector)
        db.session.commit()
        flash('Sector created!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/sector_form.html')

@bp.route('/block/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_block():
    sectors = Sector.query.all()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        sector_id = request.form['sector_id']
        block = Block(name=name, description=description, sector_id=sector_id)
        db.session.add(block)
        db.session.commit()
        flash('Block created!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/block_form.html', sectors=sectors)

@bp.route('/boulder/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_boulder():
    blocks = Block.query.all()
    tags = Tag.query.order_by(Tag.name).all()
    if request.method == 'POST':
        name = request.form.get('name')
        grade = 'V' + request.form.get('grade')
        description = request.form.get('description')
        block_id = request.form.get('block_id')
        tag_ids = request.form.getlist('tags')
        image_file = request.files.get('image')
        boulder = Boulder(
            name=name,
            grade=grade,
            description=description,
            block_id=block_id
        )
        # Handle tags
        for tag_id in tag_ids:
            tag = Tag.query.get(int(tag_id))
            if tag:
                boulder.tags.append(tag)
        # Handle image
        if image_file and image_file.filename:
            filename = save_image(image_file)
            boulder.image_path = filename
        db.session.add(boulder)
        db.session.commit()
        flash('Boulder created!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/boulder_form.html', blocks=blocks, tags=tags)

@bp.route('/sectors')
@login_required
@admin_required
def sectors_table():
    sectors = Sector.query.all()
    return render_template('admin/sectors_table.html', sectors=sectors)

@bp.route('/blocks')
@login_required
@admin_required
def blocks_table():
    blocks = Block.query.all()
    return render_template('admin/blocks_table.html', blocks=blocks)

@bp.route('/boulders')
@login_required
@admin_required
def boulders_table():
    boulders = Boulder.query.all()
    return render_template('admin/boulders_table.html', boulders=boulders)

@bp.route('/sector/edit/<int:sector_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_sector(sector_id):
    sector = Sector.query.get_or_404(sector_id)
    if request.method == 'POST':
        sector.name = request.form['name']
        sector.description = request.form.get('description', '')
        db.session.commit()
        flash('Sector updated!')
        return redirect(url_for('admin.sectors_table'))
    return render_template('admin/sector_form.html', sector=sector, edit=True)

@bp.route('/block/edit/<int:block_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_block(block_id):
    block = Block.query.get_or_404(block_id)
    sectors = Sector.query.all()
    if request.method == 'POST':
        block.name = request.form['name']
        block.description = request.form.get('description', '')
        block.sector_id = request.form['sector_id']
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = save_image(image_file)
            block.image_path = filename
        db.session.commit()
        flash('Block updated!')
        return redirect(url_for('admin.blocks_table'))
    return render_template('admin/block_form.html', block=block, sectors=sectors, edit=True)

@bp.route('/boulder/edit/<int:boulder_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_boulder(boulder_id):
    boulder = Boulder.query.get_or_404(boulder_id)
    blocks = Block.query.all()
    tags = Tag.query.order_by(Tag.name).all()
    if request.method == 'POST':
        boulder.name = request.form.get('name')
        boulder.grade = 'V' + request.form.get('grade')
        boulder.description = request.form.get('description')
        boulder.block_id = request.form.get('block_id')
        tag_ids = request.form.getlist('tags')
        # Update tags
        boulder.tags.clear()
        for tag_id in tag_ids:
            tag = Tag.query.get(int(tag_id))
            if tag:
                boulder.tags.append(tag)
        # Handle image
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = save_image(image_file)
            boulder.image_path = filename
        db.session.commit()
        flash('Boulder updated!')
        return redirect(url_for('admin.boulders_table'))
    return render_template('admin/boulder_form.html', boulder=boulder, blocks=blocks, tags=tags, edit=True)

@bp.route('/sector/delete/<int:sector_id>', methods=['POST'])
@login_required
@admin_required
def delete_sector(sector_id):
    sector = Sector.query.get_or_404(sector_id)
    db.session.delete(sector)
    db.session.commit()
    flash('Sector deleted!')
    return redirect(url_for('admin.sectors_table'))

@bp.route('/block/delete/<int:block_id>', methods=['POST'])
@login_required
@admin_required
def delete_block(block_id):
    block = Block.query.get_or_404(block_id)
    db.session.delete(block)
    db.session.commit()
    flash('Block deleted!')
    return redirect(url_for('admin.blocks_table'))

@bp.route('/boulder/delete/<int:boulder_id>', methods=['POST'])
@login_required
@admin_required
def delete_boulder(boulder_id):
    boulder = Boulder.query.get_or_404(boulder_id)
    db.session.delete(boulder)
    db.session.commit()
    flash('Boulder deleted!')
    return redirect(url_for('admin.boulders_table'))

@bp.route('/boulders/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_boulders():
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if not file or not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'danger')
            return redirect(url_for('admin.import_boulders'))
        try:
            df = pd.read_csv(file)
            required_columns = {'name', 'grade', 'description', 'block'}
            if not required_columns.issubset(df.columns):
                flash('CSV must have columns: name, grade, description, block', 'danger')
                return redirect(url_for('admin.import_boulders'))
            for _, row in df.iterrows():
                block = Block.query.filter_by(name=row['block']).first()
                if not block:
                    flash(f"Block '{row['block']}' not found. Skipping boulder '{row['name']}'.", 'warning')
                    continue
                boulder = Boulder(
                    name=row['name'],
                    grade=row['grade'],
                    description=row.get('description', ''),
                    block_id=block.id
                )
                # Handle tags if present
                if 'tags' in df.columns and pd.notna(row.get('tags', None)):
                    tag_names = [t.strip() for t in str(row['tags']).split(',')]
                    for tag_name in tag_names:
                        if not tag_name:
                            continue
                        tag = Tag.query.filter_by(name=tag_name).first()
                        if not tag:
                            tag = Tag(name=tag_name)
                            db.session.add(tag)
                            db.session.flush()  # Get tag.id before commit
                        boulder.tags.append(tag)
                db.session.add(boulder)
            db.session.commit()
            flash('Boulders imported successfully!', 'success')
            return redirect(url_for('admin.boulders_table'))
        except Exception as e:
            flash(f'Error importing CSV: {e}', 'danger')
            return redirect(url_for('admin.import_boulders'))
    return render_template('admin/boulder_csv_import.html')

@bp.route('/tag/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_tag():
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Tag name cannot be empty.', 'danger')
        elif Tag.query.filter_by(name=name).first():
            flash('Tag already exists.', 'warning')
        else:
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.commit()
            flash('Tag created!', 'success')
            return redirect(url_for('admin.create_tag'))
    return render_template('admin/tag_form.html')

@bp.route('/tags')
@login_required
@admin_required
def tags_table():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('admin/tags_table.html', tags=tags)

@bp.route('/tag/delete/<int:tag_id>', methods=['POST'])
@login_required
@admin_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted!')
    return redirect(url_for('admin.tags_table'))

@bp.route('/boulders/delete-all', methods=['POST'])
@login_required
@admin_required
def delete_all_boulders():
    try:
        # Delete all boulders
        Boulder.query.delete()
        db.session.commit()
        flash('All boulders have been deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting boulders: ' + str(e), 'danger')
    
    return redirect(url_for('admin.boulders_table'))

def save_image(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None 