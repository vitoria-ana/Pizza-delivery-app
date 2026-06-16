from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
# Importa os decoradores de métodos HTTP
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from .models import PizzaModel, CustomerModel, OrderModel

# Create your views here.

@require_GET
def adminloginview(request):
    return render(request, "pizzaapp/adminlogin.html")

@require_POST
def authenticateadmin(request):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)

    # user exists
    if user is not None and user.username == "admin":
        login(request, user)
        return redirect('adminhomepage')

    # user doesnt exists
    if user is None:
        messages.add_message(request, messages.ERROR, "invalid credentials")
        return redirect('adminloginpage')

@require_GET
def adminhomepageview(request):
    context = {'pizzas': PizzaModel.objects.all()}
    return render(request, "pizzaapp/adminhomepage.html", context)

@require_http_methods(["GET", "POST"])
def logoutadmin(request):
    logout(request)
    return redirect('adminloginpage')

@require_POST
def addpizza(request):
    name = request.POST['pizza']
    price = request.POST['price']
    PizzaModel(name=name, price=price).save()
    return redirect('adminhomepage')

@require_POST
def deletepizza(request, pizzapk):
    PizzaModel.objects.filter(id=pizzapk).delete()
    return redirect('adminhomepage')

@require_GET
def homepageview(request):
    return render(request, "pizzaapp/homepage.html")

@require_POST
def signupuser(request):
    username = request.POST['username']
    password = request.POST['password']
    phoneno = request.POST['phoneno']

    if User.objects.filter(username=username).exists():
        messages.add_message(request, messages.ERROR, "user already exists")
        return redirect('homepage')

    User.objects.create_user(username=username, password=password).save()
    lastobject = len(User.objects.all()) - 1
    CustomerModel(userid=User.objects.all()[int(lastobject)].id, phoneno=phoneno).save()
    messages.add_message(request, messages.ERROR, "user succesfully created")
    return redirect('homepage')

@require_GET
def userloginview(request):
    return render(request, "pizzaapp/userlogin.html")

@require_POST
def userauthenticate(request):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)

    # user exists
    if user is not None:
        login(request, user)
        return redirect('customerpage')

    # user doesnt exists
    if user is None:
        messages.add_message(request, messages.ERROR, "invalid credentials")
        return redirect('userloginpage')

@require_GET
def customerwelcomeview(request):
    if not request.user.is_authenticated:
        return redirect('userloginpage')

    username = request.user.username
    context = {'username': username, 'pizzas': PizzaModel.objects.all()}
    return render(request, 'pizzaapp/customerwelcome.html', context)

@require_http_methods(["GET", "POST"])
def userlogout(request):
    logout(request)
    return redirect('userloginpage')

@require_POST
def placeorder(request):
    if not request.user.is_authenticated:
        return redirect('userloginpage')

    username = request.user.username
    phoneno = CustomerModel.objects.filter(userid=request.user.id)[0].phoneno
    address = request.POST['address']
    ordereditems = ""
    for pizza in PizzaModel.objects.all():
        pizzaid = pizza.id
        name = pizza.name
        price = pizza.price

        quantity = request.POST.get(str(pizzaid), " ")

        if str(quantity) != "0" and str(quantity) != " ":
            ordereditems = ordereditems + name + " " + "price : " + str(int(quantity) * int(price)) + " " + "quantity : " + quantity + "    "

    OrderModel(username=username, phoneno=phoneno, address=address, ordereditems=ordereditems).save()
    messages.add_message(request, messages.ERROR, "order succesfully placed")
    return redirect('customerpage')

@require_GET
def userorders(request):
    orders = OrderModel.objects.filter(username=request.user.username)
    context = {'orders': orders}
    return render(request, 'pizzaapp/userorders.html', context)

@require_GET
def adminorders(request):
    orders = OrderModel.objects.all()
    context = {'orders': orders}
    return render(request, 'pizzaapp/adminorders.html', context)

@require_POST
def acceptorder(request, orderpk):
    order = OrderModel.objects.filter(id=orderpk)[0]
    order.status = "accepted"
    order.save()
    return redirect(request.META['HTTP_REFERER'])

@require_POST
def declineorder(request, orderpk):
    order = OrderModel.objects.filter(id=orderpk)[0]
    order.status = "declined"
    order.save()
    return redirect(request.META['HTTP_REFERER'])