from django.shortcuts import render
from django.contrib.auth import authenticate, logout as log_out, login as my_login
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Food, ConsumedFood
from django.contrib import messages
from datetime import datetime
from decimal import Decimal

# food search auto fills a list with max 10 items based on entered search criteria
def my_autocomplete(request):
    if 'term' in request.GET:
        qs = Food.objects.filter(name__icontains=request.GET.get('term'))[:10]
        names = list()
        for food in qs:
            names.append(food.name)
        return JsonResponse(names, safe=False)
    return JsonResponse([], safe=False)


# homepage display
def index(request):
    if request.user.is_authenticated:
        today_total_Calories = 0
        today_total_Protein = 0
        today_total_Fat = 0
        today_total_Carb = 0
        today_total_Calories_Remaining = 2000

 
        now = datetime.now()
        # create a list of ConsumedFood objects to view for the current day
        today_consumed_foods = ConsumedFood.objects.filter(consumer=request.user, date_time__day=now.day)


        for consumed_food in today_consumed_foods:
            # quantity here is the amount in grams that the user has input for each food they have consumed
            quantity = consumed_food.quantity
            # 1. this will handle any instances where serving weight is listed as 0 in the .csv/database
            # 2.this will prevent divide by zero errors by setting serving weight to an average serving size of 100grams
            # 3. only a temporary fix until database can be updated with correct data
            if consumed_food.food.serving_weight == 0:
                serving_weight = 100
            else:
                serving_weight = consumed_food.food.serving_weight

        # formula here is quantity consumed / serving weight to get %of serving size consumed which is then
        # multiplied by calories/protein/fat/carb per serving to get correct total calories/protein/fat/carb consumed

            today_total_Calories = today_total_Calories + Decimal(Decimal(quantity/serving_weight)
                                                                  * consumed_food.food.calories)
            today_total_Protein = today_total_Protein + Decimal(Decimal(quantity/serving_weight)
                                                                * consumed_food.food.protein)
            today_total_Fat = today_total_Fat + Decimal(Decimal(quantity/serving_weight)*consumed_food.food.fat)
            today_total_Carb = today_total_Carb + Decimal(Decimal(quantity/serving_weight)*consumed_food.food.net_carbs)
            today_total_Calories_Remaining = 2000 - today_total_Calories
            
    # round totals to 2 decimal places
        today_total_Calories = round(today_total_Calories, 2)
        today_total_Protein = round(today_total_Protein, 2)
        today_total_Fat = round(today_total_Fat, 2)
        today_total_Carb = round(today_total_Carb, 2)
        today_total_Calories_Remaining = round(today_total_Calories_Remaining, 2)

        context = {
            'today_breakfasts': today_consumed_foods.filter(food_category='Breakfast'),
            'today_lunches': today_consumed_foods.filter(food_category='Lunch'),
            'today_dinners': today_consumed_foods.filter(food_category='Dinner'),
            'today_snacks': today_consumed_foods.filter(food_category='Snacks'),
            
            'today_total_Calories': today_total_Calories,
            'today_total_Protein': today_total_Protein,
            'today_total_Fat': today_total_Fat,
            'today_total_Carb': today_total_Carb,
            'today_total_Calories_Remaining': today_total_Calories_Remaining,
        }
    else:
        context={}
    return render(request, 'base/index.html', context)

#user login
def login(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            my_login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, 'Invalid username and/or password.')
            return render(request, "base/auth/login.html")
    else:
        return render(request, "base/auth/login.html")


def logout_view(request):
    log_out(request)
    return render(request, "base/auth/logout.html")

def help(request):
    return render(request, "base/help.html")


#user registration
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        # Ensure password matches confirmation password entered
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "base/auth/register.html", {
                "message": "Passwords do not match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        except IntegrityError:
            return render(request, "base/auth/register.html")
        my_login(request, user)
        messages.success(request, f'Logged in as {user.username}')
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "base/auth/register.html")



# this will create a consumed food from main page form for current user
def consume_food(request):


    if request.method == 'POST':
        # 'food_category' passed from category dropdown menu on main page
        food_category = request.POST['food_category']
        # 'food_name' passed from food name search on main page
        food_name = request.POST['food_name']
        if Food.objects.filter(name=food_name).exists():
            food = Food.objects.get(name=food_name)
        else:
            messages.error(request, f'\"{food_name}\" not found, please try again ')
            return HttpResponseRedirect(reverse('index'))
        # 'quantity' passed from quantity consumed on main page
        quantity = request.POST['quantity']
        quantity = int(quantity)

        try:
            # must check that a food is not duplicated for each category, for example, category 'Breakfast' cannot
            # contain two of the same food items.  If this occures, we will prompt user to delete the value they
            # are tryign to add again and have them re-enter with the total quantity they have consumed
            if ConsumedFood.objects.filter(consumer=request.user, food_category=food_category, food=food,
                                           date_time=datetime.today()).exists():
                messages.error(request, f'\"{food_name}\" already added to \"{food_category}\" for today. Please delete'
                                        f' and re-enter correct quantity')
                return HttpResponseRedirect(reverse('index'))

            # if there are no duplicates, we can create a consumed food instance and add to user profile
            else:
                consumed_food = ConsumedFood.objects.create(consumer=request.user, food_category=food_category,
                                                            food=food, quantity=quantity, date_time=datetime.today())

            consumed_food.save()
            messages.success(request, f'Consumed {quantity}g of \"{food_name}\" on {consumed_food.date_time}')
            return HttpResponseRedirect(reverse('index'))
        except IntegrityError:
            messages.success(request, 'there was a problem, please try again')
            return render(request, "base/auth/register.html")

    return render(request, 'base/index.html')


# this handles items that user wishes to delete
def delete_consumed_food(request):

    if request.method == 'POST':
        food_name = request.POST['DeleteButton']
        food_category = request.POST.get('field')
        food = Food.objects.get(name=food_name)

        # need these parameters to ensure food item isn't deleted from all categories if consumed more than once a day
        # without category for example, if user consumed 'Watermelon' for both 'Breakfast' and 'Lunch', we would have
        # more than 1 object returned causing error
        try:
            consumed_food = ConsumedFood.objects.get(consumer=request.user, food_category=food_category,
                                                     food=food, date_time=datetime.today())
            consumed_food.delete()
            messages.success(request, f' \"{food_name}\" was deleted successfully')
            return HttpResponseRedirect(reverse('index'))
        except IntegrityError:
            messages.success(request, 'There was an issue')
            return render(request, "base/index.html")

    return render(request, 'base/index.html')




#nutrition history saved after each day ends
def nutrient_history(request):
    if request.user.is_authenticated:
        input_date = request.POST.get('input_date')
        
        date_total_Calories = 0
        date_total_Protein = 0
        date_total_Fat = 0
        date_total_Carb = 0

        date_foods = ConsumedFood.objects.filter(consumer=request.user, date_time=input_date)

        #same logic applies as in index function above
        for consumed_food in date_foods:
            quantity = consumed_food.quantity
        #prevent divide by zero errors by setting to avg serving size of 100 if database empty for serving_weight value
            if consumed_food.food.serving_weight == 0:
                serving_weight = 100
            else:
                serving_weight = consumed_food.food.serving_weight

            #total = quantity consumed(g) / serving weight (g) * (calories/protein/fat/carb per serving)
            date_total_Calories = date_total_Calories + Decimal(Decimal(quantity/serving_weight)
                                                                * consumed_food.food.calories)
            date_total_Protein = date_total_Protein + Decimal(Decimal(quantity/serving_weight)
                                                              * consumed_food.food.protein)
            date_total_Fat = date_total_Fat + Decimal(Decimal(quantity/serving_weight) * consumed_food.food.fat)
            date_total_Carb = date_total_Carb + Decimal(Decimal(quantity/serving_weight) * consumed_food.food.net_carbs)

        #round to 2 decimal places
        date_total_Calories = round(date_total_Calories, 2)
        date_total_Protein = round(date_total_Protein, 2)
        date_total_Fat = round(date_total_Fat, 2)
        date_total_Carb = round(date_total_Carb, 2)

        context = {
            'date_breakfasts': date_foods.filter(food_category='Breakfast'),
            'date_lunches': date_foods.filter(food_category='Lunch'),
            'date_dinners': date_foods.filter(food_category='Dinner'),
            'date_snacks': date_foods.filter(food_category='Snacks'),
            
            'date_total_Calories': date_total_Calories,
            'date_total_Protein': date_total_Protein,
            'date_total_Fat': date_total_Fat,
            'date_total_Carb': date_total_Carb,

            'selected_date': input_date
        }
    else:
        context = {}
    return render(request, 'base/nutrient_history.html', context)