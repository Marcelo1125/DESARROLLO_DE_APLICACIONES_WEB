from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms.password_form import PasswordForm
from forms.producto_form import ProductoForm
from forms.estudiante_form import EstudianteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm
from forms.servicio_form import ServicioForm
from datetime import date
import os
from dotenv import load_dotenv


# =========================================
# CARGAR VARIABLES DE ENTORNO
# =========================================

load_dotenv()


# =========================================
# INICIALIZACIÓN DE LA APLICACIÓN
# =========================================

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

database_url = os.getenv('DATABASE_URL')

# Compatibilidad por si Render entrega postgres://
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace(
        'postgres://',
        'postgresql://',
        1
    )

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


# =========================================
# CONFIGURACIÓN LOGIN
# =========================================

login_manager = LoginManager()

login_manager.login_view = 'login'

login_manager.init_app(app)


# =========================================
# MODELOS
# =========================================

class Producto(db.Model):

    __tablename__ = 'productos'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    precio = db.Column(
        db.Float,
        nullable=False
    )

    stock = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )


class Estudiante(db.Model):

    __tablename__ = 'estudiantes'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    apellido = db.Column(
        db.String(100),
        nullable=False
    )

    direccion = db.Column(
        db.String(200),
        nullable=False
    )

    telefono = db.Column(
        db.String(20),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        nullable=False
    )


class Proveedor(db.Model):

    __tablename__ = 'proveedores'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    empresa = db.Column(
        db.String(150),
        nullable=False
    )

    telefono = db.Column(
        db.String(20),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        nullable=False
    )


class Factura(db.Model):

    __tablename__ = 'facturas'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    fecha = db.Column(
        db.Date,
        nullable=False
    )

    # Puede ser NULL cuando el cliente es "Otro"
    estudiante_id = db.Column(
        db.Integer,
        db.ForeignKey('estudiantes.id'),
        nullable=True
    )

    cliente_nombre = db.Column(
        db.String(100),
        nullable=True
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey('productos.id'),
        nullable=True
    )

    servicio_id = db.Column(
        db.Integer,
        db.ForeignKey('servicios.id'),
        nullable=True
    )

    cantidad = db.Column(
        db.Integer,
        nullable=True
    )

    subtotal = db.Column(
        db.Float,
        nullable=False
    )

    iva = db.Column(
        db.Float,
        nullable=False
    )

    descuento = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    total = db.Column(
        db.Float,
        nullable=False
    )

    forma_pago = db.Column(
        db.String(50),
        nullable=False
    )

    estado = db.Column(
        db.String(20),
        nullable=False,
        default="Pendiente"
    )

    estudiante = db.relationship(
        'Estudiante',
        backref='facturas'
    )

    producto = db.relationship(
        'Producto',
        backref='facturas'
    )

    servicio = db.relationship(
        'Servicio',
        backref='facturas'
    )


class Servicio(db.Model):

    __tablename__ = 'servicios'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    descripcion = db.Column(
        db.String(200),
        nullable=False
    )

    precio = db.Column(
        db.Float,
        nullable=False
    )


class Usuario(db.Model, UserMixin):

    __tablename__ = 'usuarios'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(200),
        nullable=False
    )

    def set_password(self, password):

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )


@login_manager.user_loader
def load_user(user_id):

    return Usuario.query.get(int(user_id))


# =========================================
# RUTA PRINCIPAL
# =========================================

@app.route('/')
def index():

    return render_template(
        'index.html'
    )


# =========================================
# LOGIN
# =========================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(
            username=username
        ).first()

        if usuario and usuario.check_password(password):

            login_user(usuario)

            flash(
                "Inicio de sesión exitoso.",
                "success"
            )

            return redirect(
                url_for('index')
            )

        else:

            flash(
                "Usuario o contraseña incorrectos.",
                "danger"
            )

    return render_template(
        'login.html'
    )


# =========================================
# LOGOUT
# =========================================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    flash(
        "Sesión cerrada correctamente.",
        "info"
    )

    return redirect(
        url_for('index')
    )


# =========================================
# REGISTRO
# =========================================

@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if Usuario.query.filter_by(
            username=username
        ).first():

            flash(
                "Ese usuario ya existe.",
                "warning"
            )

        else:

            nuevo = Usuario(
                username=username
            )

            nuevo.set_password(
                password
            )

            db.session.add(nuevo)

            db.session.commit()

            flash(
                "Usuario registrado con éxito.",
                "success"
            )

            return redirect(
                url_for('login')
            )

    return render_template(
        'registro.html'
    )


# =========================================
# PRODUCTOS
# =========================================

@app.route('/productos')
@login_required
def productos():

    lista = Producto.query.all()

    return render_template(
        'productos.html',
        productos=lista
    )


# =========================================
# NUEVO PRODUCTO
# =========================================

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():

    form = ProductoForm()

    if form.validate_on_submit():

        nuevo = Producto(

            nombre=form.nombre.data,

            precio=form.precio.data,

            stock=form.stock.data
        )

        db.session.add(nuevo)

        db.session.commit()

        flash(
            "Producto registrado correctamente.",
            "success"
        )

        return redirect(
            url_for('productos')
        )

    return render_template(
        'formulario_producto.html',
        form=form
    )


# =========================================
# EDITAR PRODUCTO
# =========================================

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):

    producto = Producto.query.get_or_404(id)

    # -----------------------------------------
    # CONFIRMACIÓN DE CONTRASEÑA
    # -----------------------------------------

    if request.args.get('confirmar') == '1':

        form_password = PasswordForm()

        if form_password.validate_on_submit():

            usuario = Usuario.query.get(
                current_user.id
            )

            if usuario.check_password(
                form_password.password.data
            ):

                nombre = session.pop(
                    'producto_nombre',
                    None
                )

                precio = session.pop(
                    'producto_precio',
                    None
                )

                stock = session.pop(
                    'producto_stock',
                    None
                )

                if nombre is not None:
                    producto.nombre = nombre

                if precio is not None:
                    producto.precio = precio

                if stock is not None:
                    producto.stock = stock

                db.session.commit()

                flash(
                    "Producto actualizado correctamente.",
                    "success"
                )

                return redirect(
                    url_for('productos')
                )

            else:

                flash(
                    "Contraseña incorrecta. Los cambios no se guardaron.",
                    "danger"
                )

        return render_template(
            'confirmar_password.html',
            form=form_password,
            accion="editar",
            volver="productos"
        )

    # -----------------------------------------
    # FORMULARIO NORMAL
    # -----------------------------------------

    form = ProductoForm(
        obj=producto
    )

    if form.validate_on_submit():

        session['producto_nombre'] = form.nombre.data

        session['producto_precio'] = float(
            form.precio.data
        )

        session['producto_stock'] = form.stock.data

        return redirect(
            url_for(
                'editar_producto',
                id=id,
                confirmar='1'
            )
        )

    return render_template(
        'formulario_producto.html',
        form=form
    )


# =========================================
# ELIMINAR PRODUCTO
# =========================================

@app.route('/productos/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):

    producto = Producto.query.get_or_404(id)

    form_password = PasswordForm()

    if form_password.validate_on_submit():

        usuario = Usuario.query.get(
            current_user.id
        )

        if usuario.check_password(
            form_password.password.data
        ):

            db.session.delete(
                producto
            )

            db.session.commit()

            flash(
                "Producto eliminado correctamente.",
                "success"
            )

            return redirect(
                url_for('productos')
            )

        else:

            flash(
                "Contraseña incorrecta. El producto no fue eliminado.",
                "danger"
            )

    return render_template(
        'confirmar_password.html',
        form=form_password,
        accion="eliminar",
        volver="productos"
    )


# =========================================
# ESTUDIANTES
# =========================================

@app.route('/estudiantes')
@login_required
def estudiantes():

    lista = Estudiante.query.all()

    return render_template(
        'estudiantes.html',
        estudiantes=lista
    )


# =========================================
# NUEVO ESTUDIANTE
# =========================================

@app.route('/estudiantes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_estudiante():

    form = EstudianteForm()

    if form.validate_on_submit():

        nuevo = Estudiante(

            nombre=form.nombre.data,

            apellido=form.apellido.data,

            direccion=form.direccion.data,

            telefono=form.telefono.data,

            email=form.email.data
        )

        db.session.add(nuevo)

        db.session.commit()

        flash(
            "Estudiante registrado con éxito.",
            "success"
        )

        return redirect(
            url_for('estudiantes')
        )

    return render_template(
        'formulario_estudiante.html',
        form=form
    )


# =========================================
# EDITAR ESTUDIANTE
# =========================================

@app.route('/estudiantes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_estudiante(id):

    estudiante = Estudiante.query.get_or_404(id)

    if request.args.get('confirmar') == '1':

        form_password = PasswordForm()

        if form_password.validate_on_submit():

            usuario = Usuario.query.get(
                current_user.id
            )

            if usuario.check_password(
                form_password.password.data
            ):

                estudiante.nombre = session.pop(
                    'estudiante_nombre'
                )

                estudiante.apellido = session.pop(
                    'estudiante_apellido'
                )

                estudiante.direccion = session.pop(
                    'estudiante_direccion'
                )

                estudiante.telefono = session.pop(
                    'estudiante_telefono'
                )

                estudiante.email = session.pop(
                    'estudiante_email'
                )

                db.session.commit()

                flash(
                    "Estudiante actualizado con éxito.",
                    "success"
                )

                return redirect(
                    url_for('estudiantes')
                )

            else:

                flash(
                    "Contraseña incorrecta. Los cambios no se guardaron.",
                    "danger"
                )

        return render_template(
            'confirmar_password.html',
            form=form_password,
            accion="editar",
            volver="estudiantes"
        )

    form = EstudianteForm(
        obj=estudiante
    )

    if form.validate_on_submit():

        session['estudiante_nombre'] = form.nombre.data

        session['estudiante_apellido'] = form.apellido.data

        session['estudiante_direccion'] = form.direccion.data

        session['estudiante_telefono'] = form.telefono.data

        session['estudiante_email'] = form.email.data

        return redirect(
            url_for(
                'editar_estudiante',
                id=id,
                confirmar='1'
            )
        )

    return render_template(
        'formulario_estudiante.html',
        form=form
    )


# =========================================
# ELIMINAR ESTUDIANTE
# =========================================

@app.route('/estudiantes/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_estudiante(id):

    estudiante = Estudiante.query.get_or_404(id)

    form_password = PasswordForm()

    if form_password.validate_on_submit():

        usuario = Usuario.query.get(
            current_user.id
        )

        if usuario.check_password(
            form_password.password.data
        ):

            db.session.delete(
                estudiante
            )

            db.session.commit()

            flash(
                "Estudiante eliminado correctamente.",
                "info"
            )

            return redirect(
                url_for('estudiantes')
            )

        else:

            flash(
                "Contraseña incorrecta. El estudiante no fue eliminado.",
                "danger"
            )

    return render_template(
        'confirmar_password.html',
        form=form_password,
        accion="eliminar",
        volver="estudiantes"
    )


# =========================================
# PROVEEDORES
# =========================================

@app.route('/proveedores')
@login_required
def proveedores():

    lista = Proveedor.query.all()

    return render_template(
        'proveedores.html',
        proveedores=lista
    )


# =========================================
# NUEVO PROVEEDOR
# =========================================

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_proveedor():

    form = ProveedorForm()

    if form.validate_on_submit():

        nuevo = Proveedor(

            nombre=form.nombre.data,

            empresa=form.empresa.data,

            telefono=form.telefono.data,

            email=form.email.data
        )

        db.session.add(nuevo)

        db.session.commit()

        flash(
            "Proveedor registrado correctamente.",
            "success"
        )

        return redirect(
            url_for('proveedores')
        )

    return render_template(
        'formulario_proveedor.html',
        form=form
    )


# =========================================
# EDITAR PROVEEDOR
# =========================================

@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_proveedor(id):

    proveedor = Proveedor.query.get_or_404(id)

    if request.args.get('confirmar') == '1':

        form_password = PasswordForm()

        if form_password.validate_on_submit():

            usuario = Usuario.query.get(
                current_user.id
            )

            if usuario.check_password(
                form_password.password.data
            ):

                proveedor.nombre = session.pop(
                    'proveedor_nombre'
                )

                proveedor.empresa = session.pop(
                    'proveedor_empresa'
                )

                proveedor.telefono = session.pop(
                    'proveedor_telefono'
                )

                proveedor.email = session.pop(
                    'proveedor_email'
                )

                db.session.commit()

                flash(
                    "Proveedor actualizado con éxito.",
                    "success"
                )

                return redirect(
                    url_for('proveedores')
                )

            else:

                flash(
                    "Contraseña incorrecta. Los cambios no se guardaron.",
                    "danger"
                )

        return render_template(
            'confirmar_password.html',
            form=form_password,
            accion="editar",
            volver="proveedores"
        )

    form = ProveedorForm(
        obj=proveedor
    )

    if form.validate_on_submit():

        session['proveedor_nombre'] = form.nombre.data

        session['proveedor_empresa'] = form.empresa.data

        session['proveedor_telefono'] = form.telefono.data

        session['proveedor_email'] = form.email.data

        return redirect(
            url_for(
                'editar_proveedor',
                id=id,
                confirmar='1'
            )
        )

    return render_template(
        'formulario_proveedor.html',
        form=form
    )


# =========================================
# ELIMINAR PROVEEDOR
# =========================================

@app.route('/proveedores/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_proveedor(id):

    proveedor = Proveedor.query.get_or_404(id)

    form_password = PasswordForm()

    if form_password.validate_on_submit():

        usuario = Usuario.query.get(
            current_user.id
        )

        if usuario.check_password(
            form_password.password.data
        ):

            db.session.delete(
                proveedor
            )

            db.session.commit()

            flash(
                "Proveedor eliminado correctamente.",
                "info"
            )

            return redirect(
                url_for('proveedores')
            )

        else:

            flash(
                "Contraseña incorrecta. El proveedor no fue eliminado.",
                "danger"
            )

    return render_template(
        'confirmar_password.html',
        form=form_password,
        accion="eliminar",
        volver="proveedores"
    )


# =========================================
# SERVICIOS
# =========================================

@app.route('/servicios')
@login_required
def servicios():

    lista = Servicio.query.all()

    return render_template(
        'servicios.html',
        servicios=lista
    )


# =========================================
# NUEVO SERVICIO
# =========================================

@app.route('/servicios/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_servicio():

    form = ServicioForm()

    if form.validate_on_submit():

        nuevo = Servicio(

            nombre=form.nombre.data,

            descripcion=form.descripcion.data,

            precio=form.precio.data
        )

        db.session.add(nuevo)

        db.session.commit()

        flash(
            "Servicio registrado correctamente.",
            "success"
        )

        return redirect(
            url_for('servicios')
        )

    return render_template(
        'formulario_servicio.html',
        form=form
    )


# =========================================
# EDITAR SERVICIO
# =========================================

@app.route('/servicios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_servicio(id):

    servicio = Servicio.query.get_or_404(id)

    if request.args.get('confirmar') == '1':

        form_password = PasswordForm()

        if form_password.validate_on_submit():

            usuario = Usuario.query.get(
                current_user.id
            )

            if usuario.check_password(
                form_password.password.data
            ):

                servicio.nombre = session.pop(
                    'servicio_nombre'
                )

                servicio.precio = session.pop(
                    'servicio_precio'
                )

                db.session.commit()

                flash(
                    "Servicio actualizado con éxito.",
                    "success"
                )

                return redirect(
                    url_for('servicios')
                )

            else:

                flash(
                    "Contraseña incorrecta. Los cambios no se guardaron.",
                    "danger"
                )

        return render_template(
            'confirmar_password.html',
            form=form_password,
            accion="editar",
            volver="servicios"
        )

    form = ServicioForm(
        obj=servicio
    )

    if form.validate_on_submit():

        session['servicio_nombre'] = form.nombre.data

        session['servicio_precio'] = float(
            form.precio.data
        )

        return redirect(
            url_for(
                'editar_servicio',
                id=id,
                confirmar='1'
            )
        )

    return render_template(
        'formulario_servicio.html',
        form=form
    )


# =========================================
# ELIMINAR SERVICIO
# =========================================

@app.route('/servicios/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_servicio(id):

    servicio = Servicio.query.get_or_404(id)

    form_password = PasswordForm()

    if form_password.validate_on_submit():

        usuario = Usuario.query.get(
            current_user.id
        )

        if usuario.check_password(
            form_password.password.data
        ):

            db.session.delete(
                servicio
            )

            db.session.commit()

            flash(
                "Servicio eliminado correctamente.",
                "info"
            )

            return redirect(
                url_for('servicios')
            )

        else:

            flash(
                "Contraseña incorrecta. El servicio no fue eliminado.",
                "danger"
            )

    return render_template(
        'confirmar_password.html',
        form=form_password,
        accion="eliminar",
        volver="servicios"
    )


# =========================================
# FACTURACIÓN
# =========================================

@app.route('/facturacion', methods=['GET', 'POST'])
@login_required
def facturacion():

    if request.method == "POST":

        # -----------------------------------------
        # ESTUDIANTE / CLIENTE
        # -----------------------------------------

        estudiante_select = request.form.get(
            "estudiante"
        )

        cliente_nombre = request.form.get(
            "cliente_nombre"
        )

        estudiante_id = None

        # Cliente "Otro"
        if estudiante_select == "otro":

            if not cliente_nombre or not cliente_nombre.strip():

                flash(
                    "Ingrese el nombre del cliente.",
                    "danger"
                )

                return redirect(
                    url_for('facturacion')
                )

            cliente_nombre = cliente_nombre.strip()

        # Estudiante
        elif estudiante_select:

            try:

                estudiante_id = int(
                    estudiante_select
                )

            except ValueError:

                flash(
                    "Estudiante seleccionado no válido.",
                    "danger"
                )

                return redirect(
                    url_for('facturacion')
                )

            estudiante = Estudiante.query.get(
                estudiante_id
            )

            if not estudiante:

                flash(
                    "El estudiante seleccionado no existe.",
                    "danger"
                )

                return redirect(
                    url_for('facturacion')
                )

        else:

            flash(
                "Seleccione un estudiante o cliente.",
                "danger"
            )

            return redirect(
                url_for('facturacion')
            )

        # -----------------------------------------
        # PRODUCTO
        # -----------------------------------------

        producto_id = request.form.get(
            "producto"
        ) or None

        # -----------------------------------------
        # SERVICIO
        # -----------------------------------------

        servicio_id = request.form.get(
            "servicio"
        ) or None

        # -----------------------------------------
        # CANTIDAD
        # -----------------------------------------

        cantidad = request.form.get(
            "cantidad"
        )

        try:

            cantidad = int(
                cantidad
            ) if cantidad else 1

        except ValueError:

            cantidad = 1

        if cantidad < 1:

            cantidad = 1

        # -----------------------------------------
        # FORMA DE PAGO
        # -----------------------------------------

        forma_pago = request.form.get(
            "forma_pago"
        )

        if not forma_pago:

            flash(
                "Seleccione una forma de pago.",
                "danger"
            )

            return redirect(
                url_for('facturacion')
            )

        # -----------------------------------------
        # VALIDAR PRODUCTO / SERVICIO
        # -----------------------------------------

        if not producto_id and not servicio_id:

            flash(
                "Seleccione un producto o un servicio.",
                "danger"
            )

            return redirect(
                url_for('facturacion')
            )

        # -----------------------------------------
        # CALCULAR SUBTOTAL
        # -----------------------------------------

        subtotal = 0.0

        producto = None
        servicio = None

        # -----------------------------------------
        # PRODUCTO + STOCK
        # -----------------------------------------

        if producto_id:

            try:

                producto_id_int = int(
                    producto_id
                )

            except ValueError:

                flash(
                    "Producto seleccionado no válido.",
                    "danger"
                )

                return redirect(
                    url_for('facturacion')
                )

            producto = Producto.query.get(
                producto_id_int
            )

            if not producto:

                flash(
                    "El producto seleccionado no existe.",
                    "danger"
                )

                return redirect(
                    url_for('facturacion')
                )

            if producto.stock < cantidad:

                flash(
                    f"Stock insuficiente. Solo quedan "
                    f"{producto.stock} unidad(es) de "
                    f"{producto.nombre}.",
                    "danger"
                )

                return redirect(
                    url_for('facturacion')
                )

            subtotal += (
                float(producto.precio)
                * cantidad
            )

        # -----------------------------------------
        # SERVICIO
        # -----------------------------------------

        if servicio_id:

            try:

                servicio_id_int = int(
                    servicio_id
                )

            except ValueError:

                flash(
                    "Servicio seleccionado no válido.",
                    "danger"
                )

                return redirect(
                    url_for('facturacion')
                )

            servicio = Servicio.query.get(
                servicio_id_int
            )

            if not servicio:

                flash(
                    "El servicio seleccionado no existe.",
                    "danger"
                )

                return redirect(
                    url_for('facturacion')
                )

            subtotal += float(
                servicio.precio
            )

        # -----------------------------------------
        # DESCUENTO / IVA
        # -----------------------------------------

        descuento = 0.0

        iva = (
            subtotal - descuento
        ) * 0.15

        total = (
            subtotal
            - descuento
            + iva
        )

        # -----------------------------------------
        # CREAR FACTURA
        # -----------------------------------------

        nueva = Factura(

            fecha=date.today(),

            estudiante_id=estudiante_id,

            cliente_nombre=(
                cliente_nombre
                if estudiante_select == "otro"
                else None
            ),

            producto_id=(
                int(producto_id)
                if producto_id
                else None
            ),

            servicio_id=(
                int(servicio_id)
                if servicio_id
                else None
            ),

            cantidad=cantidad,

            subtotal=subtotal,

            iva=iva,

            descuento=descuento,

            total=total,

            forma_pago=forma_pago,

            estado="Pendiente"
        )

        # -----------------------------------------
        # DESCONTAR STOCK
        # -----------------------------------------

        if producto:

            producto.stock -= cantidad

        # -----------------------------------------
        # GUARDAR
        # -----------------------------------------

        db.session.add(nueva)

        db.session.commit()

        flash(
            "Factura registrada con éxito. Stock actualizado.",
            "success"
        )

        return redirect(
            url_for('facturas')
        )

    # -----------------------------------------
    # DATOS PARA EL FORMULARIO
    # -----------------------------------------

    productos = Producto.query.all()

    servicios = Servicio.query.all()

    estudiantes = Estudiante.query.all()

    return render_template(

        "formulario_facturacion.html",

        productos=productos,

        servicios=servicios,

        estudiantes=estudiantes
    )


# =========================================
# LISTA DE FACTURAS
# =========================================

@app.route('/facturas')
@login_required
def facturas():

    lista = Factura.query.order_by(
        Factura.id.desc()
    ).all()

    return render_template(
        'facturas.html',
        facturas=lista
    )


# =========================================
# DETALLE / IMPRIMIR FACTURA
# =========================================

@app.route('/facturas/<int:id>')
@login_required
def factura_detalle(id):

    factura = Factura.query.get_or_404(
        id
    )

    return render_template(
        'facturas_detalle.html',
        factura=factura
    )


# =========================================
# BLOQUE DE ARRANQUE
# =========================================

if __name__ == '__main__':

    app.run(
        debug=True
    )