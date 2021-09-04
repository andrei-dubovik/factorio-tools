"""Routines for loading and standardizing Factorio recipes."""

# Load packages

# Standard library
import json
from copy import copy
from itertools import product
from collections import namedtuple


# Define category substitutions
CATEGORY = {
    'advanced-crafting': 'crafting',  # legacy category?
    'crafting-with-fluid': 'crafting',  # mostly irrelevant distinction
}

# Define named tuples
Technology = namedtuple(
    'technology', ['name', 'category', 'inputs', 'outputs', 'time']
)

Item = namedtuple('item', ['name', 'type', 'amount'])


def select_mode(recipe, mode):
    """Select 'expensive' or 'normal' mode as default."""
    if mode in recipe:
        return {**recipe, **recipe[mode]}
    else:
        return recipe


def pluralize_result(recipe):
    """Standardize 'result' to 'results'."""
    if result := recipe.get('result'):
        recipe = copy(recipe)
        del recipe['result']
        count = recipe.pop('result_count', 1)
        recipe['results'] = [[result, count]]
    return recipe


def add_defaults(recipe):
    """Add default values explicitly."""
    recipe = copy(recipe)
    recipe.setdefault('energy_required', 0.5)
    cat = recipe.get('category', 'crafting')
    recipe['category'] = CATEGORY.get(cat, cat)
    return recipe


def convert_item(item):
    """Convert lists or dictionaries to named tuples, drop extra details."""
    if type(item) == list:
        return Item(item[0], 'item', item[1])
    if type(item) == dict:
        item_type = item.get('type', 'item')
        amount = item['amount']
        prob = item.get('probability', 1)
        return Item(item['name'], item_type, amount*prob)
    

def convert_recipe(recipe):
    """Convert a dictionary to a named tuple, change field names."""
    return Technology(
        recipe['name'],
        recipe['category'],
        [convert_item(r) for r in recipe['ingredients']],
        [convert_item(r) for r in recipe['results']],
        recipe['energy_required']
    )


def load_recipes(path, mode):
    """Load recipes from a json file."""
    with open(path) as file:
        recipes = json.load(file)
    recipes = [pluralize_result(select_mode(r, mode)) for r in recipes]
    recipes = [convert_recipe(add_defaults(r)) for r in recipes]
    return recipes
