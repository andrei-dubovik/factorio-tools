"""Functions to pretty print calculation results."""

# Load packages

# Standard library
import math

# External libraries
import tabulate
tabulate.PRESERVE_WHITESPACE = True


# TODO: add rounding option to print functions
def sym_ceil(x, tol=1e-08):
    """Round down for negative, round up for positive."""
    if abs(x - round(x)) < tol:
        return round(x)
    elif x > 0:
        return math.ceil(x)
    else:
        return math.floor(x)


def default_speed():
    """Return starting crafting speeds per category."""
    return {
        'crafting': 0.5,
        'chemistry': 1.0,
        'smelting': 1.0,
        'centrifuging': 1.0,
        'oil-processing': 1.0,
        'rocket-building': 1.0,
    }


def print_io(technologies, speed=default_speed()):
    """Print per-facility input/output requirements."""
    headers = ['name', 'direction', 'items/s', 'type']
    rows = []
    for t in technologies:
        time = t.time / speed[t.category]
        rows.append([t.name])
        for items, lbl in [(t.inputs, 'in'), (t.outputs, 'out')]:
            for name, item_type, amount in items:
                flow = amount / time
                rows.append(['  ' + name, lbl, flow, item_type])
    print(tabulate.tabulate(rows, headers=headers))


def print_technologies(technologies, speed=default_speed()):
    """Print technologies, indicate the number of required facilities."""
    headers = [
        'name', 'cycles/s\n(machine)', 'cycles\n(demand)', 'time or count'
    ]
    rows = []
    for t in technologies:
        cycles = speed[t.category] / t.time
        count = t.cycles / cycles
        rows.append([t.name, cycles, t.cycles, count])
    print(tabulate.tabulate(rows, headers=headers))


def print_flows(flows):
    """Print aggregate flows."""
    headers = ['name', 'amount', 'type']
    rows = []

    def print_group(name, items):
        rows.append([name])
        for name, item_type, amount in items:
            rows.append(['  ' + name, amount, item_type])

    for name, items in zip(flows._fields, flows):
        print_group(name, items)

    print(tabulate.tabulate(rows, headers=headers))
