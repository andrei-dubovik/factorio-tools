"""Productivity and speed transformations."""

# Local libraries
from common import update
from recipes import Item, Technology


def adjust_speed(technology, factor):
    """Adjust crafting speed for a given technology."""
    return Technology(**update(technology, time=technology.time/factor))


def adjust_productivity(technology, factor):
    """Adjust productivity for a given technology."""
    outputs = [Item(**update(i, amount=i.amount*factor)) for i in technology.outputs]
    return Technology(**update(technology, outputs=outputs))


def adjust_all(technology, speed, productivity):
    """Adjust crafting speed and productivity for a given technology."""
    if speed := speed.get(technology.category):
        technology = adjust_speed(technology, speed)
    if productivity := productivity.get(technology.category):
        technology = adjust_productivity(technology, productivity)
    return technology


def adjust(technologies, speed={}, productivity={}, test=lambda t: True):
    """Adjust crafting speed and productivity for a group of technologies."""
    return [adjust_all(t, speed, productivity) if test(t) else t for t in technologies]
