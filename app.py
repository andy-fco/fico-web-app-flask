from flask import Flask, render_template

app = Flask(__name__)


#----------RUTAS PÚBLICAS-----------#

@app.route('/')
def inicio():
    return render_template('public/index.html')

@app.route('/login')
def login():
    return render_template('auth/login.html')


@app.route('/register')
def register():
    return render_template('auth/register.html')

@app.route('/simulador')
def simulador():
    return render_template('public/simulador.html')


#----------RUTAS DASHBOARD-----------#

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard/home.html')

@app.route('/dashboard/movimientos')
def movimientos():
    return render_template('dashboard/movimientos.html')

@app.route('/dashboard/proyecciones')
def proyecciones():
    return render_template('dashboard/proyecciones.html')

@app.route('/dashboard/reportes')
def reportes():
    return render_template('dashboard/reportes.html')

@app.route('/dashboard/independencia')
def independencia():
    return render_template('dashboard/independencia.html')



if __name__ == '__main__':
    app.run(debug=True)