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


def print_io(technologies):
    """Print per-facility input/output requirements."""
    headers = ['name', 'direction', 'items/s', 'type']
    rows = []
    for t in technologies:
        rows.append([t.name])
        for items, lbl in [(t.inputs, 'in'), (t.outputs, 'out')]:
            for name, item_type, amount in items:
                flow = amount / t.time
                rows.append(['  ' + name, lbl, flow, item_type])
    print(tabulate.tabulate(rows, headers=headers))


def print_technologies(technologies):
    """Print technologies, indicate the number of required facilities."""
    headers = [
        'name', 'cycles/s\n(machine)', 'cycles\n(demand)', 'time or count'
    ]
    rows = []
    for t in technologies:
        cycles = 1 / t.time
        count = t.cycles * t.time
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
