from app import app,db,bcrypt,pub_key
from flask import render_template,redirect,request,flash,make_response,url_for,session
from forms import LoginForm,RegistrationForm
from models import Product,User,Order,Invoice
from flask_login import login_user,logout_user,current_user,login_required
import stripe
import datetime

TEMP_INV_ID = 9999

@app.route('/')
def gallery():
    return render_template("gallery.html")
    
@app.route('/home')
def home():

    if current_user.is_authenticated: 
        cookie = session.get('mycookie',None)    
        if cookie and cookie == 100000:
            print("This is Good cookie ", cookie)
            order = Order(name=session['name'],user_id=current_user.id,quantity=session['quantity'],
            price=session['price'],total=session['total'],invoice_id=TEMP_INV_ID)
            
            db.session.add(order)
            db.session.commit()
            session.pop('mycookie') 
            
        orders = Order.query.filter(Order.user_id==current_user.id and Order.invoice_id == TEMP_INV_ID).all()
        return render_template("index.html",database=Product.query.all(),orders=orders)
        
    return render_template("index.html",database=Product.query.all())

@app.route('/thanks')
@login_required
def thanks():
    flash('Order Placed Successfully','success')
    return redirect(url_for('invoice'))

@app.route('/login',methods=['GET','POST'])
def login():
    #for key,value in session.items():
        #print("Key = ",key,"before login Value = ",value)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print ()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('login'))
        else:
            flash('Login Unsuccesful. Please check email and password','danger')
    return render_template('login.html',title='login',form=form)

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been created ! You are now enabled to log in!','success')
        return redirect(url_for('login'))
        
    return render_template('register.html',title='Register',form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/addproduct',methods=['GET','POST'])
@login_required
def addproduct():
    if request.method=='POST':
        new_product = Product(name=request.form['name'],img=request.form['image'],price=request.form['price'])
        print(new_product)
        db.session.add(new_product)
        db.session.commit()
        return render_template("index.html",database=Product.query.all())
    return render_template("addproduct.html")

@app.route('/delete/product/<int:id>',methods=['GET','POST'])
@login_required
def delproduct(id):
    remove_product = Product.query.get_or_404(id)
    print(remove_product)
    db.session.delete(remove_product)
    db.session.commit()
    return render_template("index.html",database=Product.query.all())
    
@app.route('/orders/<int:id>',methods=['POST'])
def addorders(id):
    queryProduct = Product.query.get_or_404(id)
    #print("myQuant = ",list(request.form.keys()),request.form['quantity'])
    price = float(queryProduct.price)
    quantity = float(request.form['quantity'])
    total = price*quantity

    print("Current User ID = ",current_user.is_anonymous)
    if current_user.is_anonymous:
        user_id = 100000

    else:
        user_id = current_user.get_id()
    

    order = Order(name=queryProduct.name,user_id=user_id,quantity=quantity,price=price,total=total,invoice_id=TEMP_INV_ID)
    if current_user.is_authenticated: 
        try:
            
            db.session.add(order)
            db.session.commit()
            flash("You ordered product " + order.name,"success")
            return redirect(url_for('home')) 
        except Exception as e:
            return "There was an error updating the database " + str(e)
    else:
        flash(f"Please Login Now","warning")
        
        response = redirect(url_for('login')) 
        #response.set_cookie('YourSessionCookie',)
        session["mycookie"] = user_id
        session["price"] = price
        session["total"] = total
        session["quantity"] = quantity
        session["name"] = queryProduct.name

        for key,value in session.items():
            print("Key = ",key,"before redirect Value = ",value)
        return make_response(response)

@app.route('/delete/orders/<int:id>')
def deleteOrder(id):
    queryOrder = Order.query.get_or_404(id)
    db.session.delete(queryOrder)
    db.session.commit()
    flash("Order deleted successfully", "danger")
    return redirect(url_for('home'))

@app.route('/invoice',methods=['GET','POST'])
@login_required
def invoice():
    if request.method=='POST':
        dirty_invoice = Invoice.query.filter(Invoice.user_id == current_user.id,Invoice.payment_status == 'unpaid').first()
        if dirty_invoice:
            print("dirty_invoice = ",dirty_invoice)
            db.session.delete(dirty_invoice)
            db.session.commit()
            orders = Order.query.filter(Order.user_id == current_user.id,Order.invoice_id == None).all()
            if orders:
                for order in orders:
                    db.session.delete(order)
                db.session.commit()
        orders = Order.query.filter(Order.user_id == current_user.id,Order.invoice_id == TEMP_INV_ID).all()
        if orders:
            total = 0
            for order in orders:
                total += order.total
            timestamp=datetime.datetime.now()
            invoice = Invoice(user_id=current_user.id,timestamp=timestamp,total=total,payment_status='unpaid',order_status='created')
            db.session.add(invoice)
            db.session.commit()
            orders = Order.query.filter(Order.user_id==current_user.id).all()
            return render_template('invoice.html',invoices=Invoice.query.filter(Invoice.user_id==current_user.id).all(),
            orders = orders,pub_key=pub_key)
        else:
            flash("Please add atleast 1 item to your cart ! ","danger")
            return redirect(url_for('home'))
            #return "<script>alert('Please add atleast 1 item to your cart ! ')</script>"
    else :
        orders = Order.query.filter(Order.user_id==current_user.id).all()
        return render_template('invoice.html',invoices=Invoice.query.filter(Invoice.user_id==current_user.id).all(),
        orders=orders,pub_key=pub_key)

@app.route('/pay/<int:invoice_id>/<float:amt>',methods=['POST'])
@login_required
def pay(invoice_id,amt):
    
    print(request.form)
    customer = stripe.Customer.create(email=request.form['stripeEmail'],source=request.form["stripeToken"])
    amt = int(amt)
    charge = stripe.Charge.create(
        customer = customer.id,
        amount = amt,
        currency = 'usd',
        description = "The Product"
    )
    
    current_invoice = Invoice.query.filter(Invoice.id == invoice_id).first()
    current_invoice.payment_status = 'paid'
    current_invoice.order_status = 'received'

    user_id = current_user.get_id()
    entries = db.session.query(Order).filter(Order.invoice_id==TEMP_INV_ID,Order.user_id==user_id).all()
    
    if entries:
        #flash("Hey entry found" + str(entries[0]))
        try:
            for entry in entries:
                db.session.delete(entry)
        except Exception as e:
            print("Could not delete entry from database " + str(e))
    db.session.commit()
    
    return redirect(url_for('invoice'))

