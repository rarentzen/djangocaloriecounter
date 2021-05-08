from django.db import models
from django.contrib.auth.models import User

# Django Models are similar to objects/classes

# MAIN FOOD MODEL
# data obtained from 'my_food/MyFoodData-Nutrition-Facts-SpreadSheet-Release-1-4.csv'
# attached to project in main project folder (imported with customizable pycharm DB import feature)
# food_group = not used in this project, kept for database clarity purposes -certain food items were obscure
# additional field helped identify eg. (food name "Zombie" is obscure, associated food_group identifier shows it as
# a "Beverage" - may want to use/implement this field at a later date
#
# calories, fat, protein, net_carbs are all PER SERVING
# serving weight is weight of serving in grams

# (Requirement 1.1.0)

class Food(models.Model):
    name = models.CharField(max_length=300)
    food_group = models.CharField(max_length=100)
    calories = models.IntegerField()
    fat = models.DecimalField(decimal_places=2, max_digits=6)
    protein = models.DecimalField(decimal_places=2, max_digits=6)
    net_carbs = models.DecimalField(decimal_places=2, max_digits=6)
    serving_weight = models.DecimalField(decimal_places=2, max_digits=6)

    def __str__(self):
        return self.name
    
# consumed food model will be used to store all user food data for current date as well as history
#
class ConsumedFood(models.Model):
    # Food categories to separate meals (Requirement 1.2.2)
    CATEGORIES = (
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
        ('Snacks', 'Snacks'),
    )
    consumer = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateField(auto_now_add=True)
    food_category = models.CharField(max_length=100, choices=CATEGORIES)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.food.name


