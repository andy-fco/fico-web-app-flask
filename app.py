from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)