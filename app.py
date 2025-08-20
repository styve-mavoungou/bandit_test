from flask import Flask, render_template, redirect, url_for, request, flash, Response, session
from models import db, Student, User
from forms import StudentForm, RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SECRET_KEY'] = 'secret'
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students')
def student_list():
    students = Student.query.all()
    return render_template('student_list.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(name=form.name.data, email=form.email.data)
        db.session.add(student)
        db.session.commit()
        flash('Étudiant ajouté avec succès.')
        return redirect(url_for('student_list'))
    return render_template('add_student.html', form=form)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    if form.validate_on_submit():
        student.name = form.name.data
        student.email = form.email.data
        db.session.commit()
        flash('Informations modifiées avec succès.')
        return redirect(url_for('student_list'))
    return render_template('edit_student.html', form=form)

@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Étudiant supprimé.')
    return redirect(url_for('student_list'))

@app.route('/student/<int:id>')
def student_detail(id):
    student = Student.query.get_or_404(id)
    return render_template('student_detail.html', student=student)

@app.route('/export_csv')
def export_csv():
    students = Student.query.all()
    output = "Nom,Email\n"
    for s in students:
        output += f"{s.name},{s.email}\n"
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=students.csv"})

@app.route('/search', methods=['GET', 'POST'])
def search_student():
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form.get('query', '')
        results = Student.query.filter(Student.name.contains(query)).all()
    return render_template('search.html', results=results, query=query)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.', 'error')
            return redirect(url_for('register'))
        # Vérifier si l'email est déjà utilisé
        existing_email = Student.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Cet email est déjà utilisé. Veuillez en choisir un autre.', 'error')
            return redirect(url_for('register'))
        try:
            # Ajout dans la table User (authentification)
            hashed_pw = generate_password_hash(form.password.data)
            user = User(username=form.username.data, password=hashed_pw)
            db.session.add(user)
            # Ajout dans la table Student (liste des étudiants)
            student = Student(name=form.username.data, email=form.email.data)
            db.session.add(student)
            db.session.commit()
            flash('Inscription réussie. Connectez-vous.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de l\'inscription. Veuillez réessayer.', 'error')
            app.logger.error(f"Erreur lors de l'inscription: {str(e)}")
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Connexion réussie.')
            return redirect(url_for('index'))
        else:
            flash('Identifiants invalides.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Déconnexion réussie.')
    return redirect(url_for('login'))

#if __name__ == '__main__':
 #   with app.app_context():
 #       db.create_all()
 #   app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Autorise toutes les IP
