from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import Note, Category, Tag, User
from . import db
from werkzeug.security import generate_password_hash
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():

    if current_user.is_admin:
        return redirect(url_for('views.admin_panel'))

    pinned_notes = Note.query.filter_by(user_id=current_user.id, is_pinned=True).all()
    unpinned_notes = Note.query.filter_by(user_id=current_user.id, is_pinned=False).all()
   

    return render_template("home.html", user=current_user, pinned_notes=pinned_notes, unpinned_notes=unpinned_notes)


@views.route('/add_note', methods=['GET', 'POST'])
@login_required
def add_note():

    user_categories = Category.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        title = request.form.get('title')
        note_content = request.form.get('content')
        category_name = request.form.get('category_name')
        tags = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]

        if not title and not note_content:
            flash('Empty Note Discarded.', category='success')

        else:
            # Check if the category name already exists
            category = Category.query.filter_by(name=category_name, user_id=current_user.id).first()
            if category is None:
                # If the category does not exist, create a new one
                category = Category(name=category_name, user_id=current_user.id)
                db.session.add(category)
                db.session.commit()  # Commit the new category to the database

            # Create the note and associate it with the category
            new_note = Note(title=title, content=note_content, user_id=current_user.id, category_id=category.id)
            
            # Handle tags
            for tag_name in tags:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag is None:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                new_note.tags.append(tag)

            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

        return redirect(url_for("views.home"))
        

    return render_template("add_note.html", user=current_user, user_categories=user_categories)


@views.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get(note_id)

    user_categories = Category.query.filter_by(user_id=current_user.id).all()

    if not note or note.user_id != current_user.id:
        # Handle errors or unauthorized access
        flash('Note not found', category='error')
        return redirect('/')

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_content = request.form.get('content')
        new_category_name = request.form.get('category_name')
        new_tags = request.form.get('tags')

        # Check if any changes are made
        if (new_title == note.title and new_content == note.content
                and (note.category.name if note.category else '') == new_category_name
                and new_tags == ', '.join(tag.name for tag in note.tags)):
            flash('No changes made', category='info')
            return redirect(url_for('views.home'))

        note.title = new_title
        note.content = new_content

        # Update category name if it has changed
        if note.category:
            if note.category.name != new_category_name:
                existing_category = Category.query.filter_by(name=new_category_name, user_id=current_user.id).first()
                if existing_category is None:
                    # If the new category name doesn't exist, create a new one
                    existing_category = Category(name=new_category_name, user_id=current_user.id)
                    db.session.add(existing_category)
                note.category = existing_category
        else:
            if new_category_name:
                new_category = Category.query.filter_by(name=new_category_name, user_id=current_user.id).first()
                if new_category is None:
                    new_category = Category(name=new_category_name, user_id=current_user.id)
                    db.session.add(new_category)
                note.category = new_category

        # Update tags
        note.tags = []  # Clear existing tags
        if new_tags:
            tag_names = [tag.strip() for tag in new_tags.split(',')]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag is None:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                note.tags.append(tag)

        db.session.commit()
        flash('Note updated!', category='success')

        return redirect(url_for('views.home', note_id=note_id))

    return render_template('edit_note.html', note=note, user=current_user, user_categories=user_categories)




        

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():  
    note = json.loads(request.data) 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash('Note Deleted!', category='success')

    return jsonify({})


@views.route('/toggle-pin/<int:note_id>', methods=['POST'])
@login_required
def toggle_pin(note_id):
    note = Note.query.get(note_id)

    if note and note.user_id == current_user.id:
        note.is_pinned = not note.is_pinned
        db.session.commit()

    return '', 204  




@views.route('/manageLabels', methods=['GET'])
@login_required
def manageLabels():
    user_categories = Category.query.filter_by(user_id=current_user.id).all()
    user_tags = Tag.query.filter_by(user_id=current_user.id).all()

    return render_template('manageLabels.html', user=current_user, user_categories=user_categories, user_tags=user_tags)


@views.route('/delete-category/<int:category_id>', methods=['GET'])
@login_required
def delete_category(category_id):
    category_to_delete = Category.query.get(category_id)
    
    if category_to_delete and category_to_delete.user_id == current_user.id:
        db.session.delete(category_to_delete)
        db.session.commit()
        flash('Category deleted!', category='success')
    else:
        flash('Category not found or unauthorized.', category='error')

    return redirect(url_for('views.manageLabels'))


@views.route('/edit-category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get(category_id)

    if not category or category.user_id != current_user.id:
        flash('Category not found', category='error')
        return redirect(url_for('views.manage_notes'))

    user_categories = Category.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        new_name = request.form.get('new_name')

        # Check if the new category name already exists
        existing_category = Category.query.filter_by(name=new_name, user_id=current_user.id).first()

        if existing_category is None:
            # If the new category name doesn't exist, update the category name
            category.name = new_name
            db.session.commit()
            flash('Category updated!', category='success')
        else:
            flash('Category name already exists. Choose a different name.', category='error')

        return redirect(url_for('views.manageLabels'))

    return render_template('manageLabels.html', user=current_user, user_categories=user_categories)


@views.route('/add-category', methods=['POST'])
@login_required
def add_category():
    if request.method == 'POST':
        new_category_name = request.form.get('new_category_name')

        # Check if the category name already exists
        existing_category = Category.query.filter_by(name=new_category_name, user_id=current_user.id).first()

        if existing_category is None and new_category_name.strip() != "":
            # If the new category name doesn't exist and is not blank, create a new one
            new_category = Category(name=new_category_name, user_id=current_user.id)
            db.session.add(new_category)
            db.session.commit()
            flash('Category added!', category='success')
        else:
            flash('Category name already exists or is blank. Choose a different name.', category='error')

        return redirect(url_for('views.manageLabels'))
    
@views.route('/delete-all-notes', methods=['POST'])
@login_required
def delete_all_notes():
    # Get all notes for the current user
    notes = Note.query.filter_by(user_id=current_user.id).all()

    if not notes:
        flash('No notes to delete.', category='info')
        return redirect(url_for('views.home'))


    # Detach notes from tags and delete notes
    for note in notes:
        note.tags = [] # Detach the note from all tags
        db.session.delete(note)

    # Commit the changes
    db.session.commit()

    flash('All notes deleted!', category='success')

    return redirect(url_for('views.home'))


@views.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '')
    filter_value = request.args.get('filter', 'content')  

    search_results = []

    if filter_value == 'title':
        search_results = Note.query.filter(Note.title.ilike(f'%{query}%')).filter_by(user_id=current_user.id).all()
    elif filter_value == 'content':
        search_results = Note.query.filter(Note.content.ilike(f'%{query}%')).filter_by(user_id=current_user.id).all()
    elif filter_value == 'category':
        search_results = Note.query.join(Category).filter(Category.name.ilike(f'%{query}%')).filter_by(user_id=current_user.id).all()
    

    return render_template('search_results.html', results=search_results, user=current_user)


@views.route('/MyNotesAdmin', methods=['GET'])
@login_required
def admin_panel():

    if not current_user.is_admin:
        flash('You do not have permission to access the admin panel.', category='error')
        return redirect(url_for('views.home'))

    # Fetch all users
    users = User.query.all()

    # Find the admin user
    admin_user = next((user for user in users if user.is_admin), None)

    # Remove the admin user from the list
    users.remove(admin_user)

    # Prepend the admin user to the list
    ordered_users = [admin_user] + users

    return render_template('admin_panel.html', users=ordered_users, user=current_user)


@views.route('/manage-user/<int:user_id>', methods=['GET'])
@login_required
def manage_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to manage users.', category='error')
        return redirect(url_for('views.home'))

    users = User.query.all()  # Fetch all users

    user_to_manage = User.query.get(user_id)
    if not user_to_manage:
        flash('User not found.', category='error')
        return redirect(url_for('views.admin_panel'))

    return render_template('manage_user.html', users=users, user_to_manage=user_to_manage, user=current_user)


@views.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)  # Forbidden, as only admins can delete users

    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        # Manually delete or update associated categories
        for category in user_to_delete.categories:
            db.session.delete(category)
        # or update the user_id to NULL or another user's ID

        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User deleted!', category='success')
    else:
        flash('User not found.', category='error')

    return redirect(url_for('views.admin_panel'))

@views.route('/change-user-password/<int:user_id>', methods=['POST'])
@login_required
def change_user_password(user_id):
    if not current_user.is_admin:
        abort(403)  # Forbidden, as only admins can change user passwords

    user_to_change_password = User.query.get(user_id)
    if not user_to_change_password:
        flash('User not found.', category='error')
        return redirect(url_for('views.admin_panel'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')

        if len(new_password) < 4:
            flash("The password must be 4 characters" , category='error')

        else:
            user_to_change_password.password = generate_password_hash(new_password)  # You need to import generate_password_hash

            db.session.commit()
            flash('User password changed!', category='success')

    return redirect(url_for('views.manage_user', user_id=user_id))