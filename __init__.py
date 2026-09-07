from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms.producto_form import ProductoForm
from forms.estudiante_form import estudianteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/academia.db'
db = SQLAlchemy(app)

# MODELOS
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)

class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))

class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False)
    producto = db.Column(db.String(100), nullable=False)
    total = db.Column(db.Float, nullable=False)

# RUTAS
@app.route('/')
def index():
    return render_template('index.html')

# Productos
@app.route('/productos')
def productos():
    lista = Producto.query.all()
    return render_template('productos.html', productos=lista)

@app.route('/productos/nuevo', methods=['GET','POST'])
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        nuevo = Producto(nombre=form.nombre.data, precio=form.precio.data)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('productos'))
    return render_template('formulario_producto.html', form=form)

# Estudiantes
@app.route('/estudiantes')
def estudiantes():
    lista = Estudiante.query.all()
    return render_template('estudiantes.html', estudiantes=lista)

@app.route('/estudiantes/nuevo', methods=['GET','POST'])
def nuevo_estudiante():
    form = EstudianteForm()
    if form.validate_on_submit():
        nuevo = Estudiante(nombre=form.nombre.data, email=form.email.data)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('estudiantes'))
    return render_template('formulario_estudiante.html', form=form)

# Proveedores
@app.route('/proveedores')
def proveedores():
    lista = Proveedor.query.all()
    return render_template('proveedores.html', proveedores=lista)

@app.route('/proveedores/nuevo', methods=['GET','POST'])
def nuevo_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        nuevo = Proveedor(nombre=form.nombre.data, contacto=form.contacto.data)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('proveedores'))
    return render_template('formulario_proveedor.html', form=form)

# Facturación
@app.route('/facturacion')
def facturacion():
    lista = Factura.query.all()
    return render_template('facturacion.html', facturas=lista)

@app.route('/facturacion/nueva', methods=['GET','POST'])
def nueva_factura():
    form = FacturacionForm()
    if form.validate_on_submit():
        nueva = Factura(cliente=form.cliente.data, producto=form.producto.data, total=form.total.data)
        db.session.add(nueva)
        db.session.commit()
        return redirect(url_for('facturacion'))
    return render_template('formulario_facturacion.html', form=form)

if __name__ == '__main__':
    # Crear las tablas automáticamente si no existen
    with app.app_context():
        db.create_all()
    app.run(debug=True)
