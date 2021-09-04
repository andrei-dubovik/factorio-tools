"""Functions to find optimal production strategies."""

# Load packages

# Standard library
from itertools import product, chain, groupby
from collections import namedtuple, defaultdict

# External libraries
import numpy as np
from scipy.optimize import linprog

# Local libraries
from recipes import Item, Technology

# Define named tuples
EnumItem = namedtuple('item', ['id', *Item._fields])
OptimalTech = namedtuple(
    'technology', [*Technology._fields, 'cycles']
)
TotalFlows = namedtuple('totalflows', ['inputs', 'intermediate', 'outputs'])

def list_items(technologies):
    """List all items."""
    inputs = set(i.name for t in technologies for i in t.inputs)
    outputs = set(i.name for t in technologies for i in t.outputs)
    return inputs.union(outputs)


def list_products(technologies):
    """List intermediate and final products."""
    return set(i.name for t in technologies for i in t.outputs)


def list_resources(technologies):
    """List resources (there are no technologies that produce them)."""
    inputs = set(i.name for t in technologies for i in t.inputs)
    outputs = set(i.name for t in technologies for i in t.outputs)
    return inputs - outputs


def update(ntuple, **kwargs):
    """Update named tuple."""
    return dict(ntuple._asdict(), **kwargs)


def enumerate_items(technologies):
    """Enumerate technology/item pairs"""
    rslt = []
    j0 = 0
    for t in technologies:
        j1 = j0 + len(t.inputs)
        inputs = [EnumItem(j0 + j, *item) for j, item in enumerate(t.inputs)]
        outputs = [EnumItem(j1 + j, *item) for j, item in enumerate(t.outputs)]
        rslt.append(Technology(**update(t, inputs=inputs, outputs=outputs)))
        j0 = j1 + len(t.outputs)
    return rslt


def eq_matrices(technologies, no_vars):
    """Prepare matrices for equality constraints."""
    no_eqs = no_vars - len(technologies)
    A_eq = np.zeros((no_eqs, no_vars))    
    b_eq = np.zeros(no_eqs)

    eq = 0
    for t in technologies:
        x = product(t.inputs, t.outputs[:1])
        y = product(t.inputs[:1], t.outputs[1:])
        for (i, _, _, a), (j, _, _, b) in chain(x, y):
            A_eq[eq, i] = -b
            A_eq[eq, j] = a
            eq += 1

    return A_eq, b_eq


def ub_matrices(technologies, product_id, objectives, no_vars):
    """Prepare matrices for inequality constraints."""
    no_eqs = len(product_id)
    A_ub = np.zeros((no_eqs, no_vars))    
    b_ub = np.zeros(no_eqs)

    for t in technologies:
        for i, n, _, _ in t.inputs:
            if (j := product_id.get(n)) is not None:
                A_ub[j, i] = 1
        for i, n, _, _ in t.outputs:
            if (j := product_id.get(n)) is not None:
                A_ub[j, i] = -1

    for i, a in objectives.items():
        b_ub[product_id[i]] = -a

    return A_ub, b_ub


def default_weights(resources, multiplier=1000):
    """Construct default weights."""
    weights = defaultdict(lambda: 1)
    for r in resources:
        weights[r] = multiplier
    weights['water'] = 0
    return weights


def obj_vector(technologies, weights, no_vars):
    """Prepare the objective vector (minimizes production scale)."""
    c = np.zeros(no_vars)
    for t in technologies:
        for i, n, _, _ in t.inputs + t.outputs:
            c[i] = weights[n]
    return c


def collect_results(technologies, lp_res):
    """List necessary technologies and the number of cycles required."""
    solution = []
    for t in technologies:
        i, _, _, a = t.outputs[0]
        cycles = lp_res.x[i]/a
        if not np.isclose(cycles, 0):
            inputs = [Item(*i[1:]) for i in t.inputs]  # drop id
            outputs = [Item(*i[1:]) for i in t.outputs]  # drop id
            solution.append(OptimalTech(**update(
                t, inputs=inputs, outputs=outputs, cycles=cycles
            )))
    return solution


def aggregate_flows(technologies):
    """Aggregate flows (assume worst-case layout for intermediate products)."""
    items = defaultdict(lambda: [0, 0])
    types = {}
    for t in technologies:
        for name, item_type, amount in t.inputs:
            items[name][0] += amount*t.cycles
            types[name] = item_type
        for name, item_type, amount in t.outputs:
            items[name][1] += amount*t.cycles
            types[name] = item_type

    # Note: intermediate can overlap with inputs and outputs
    return TotalFlows(
        # Inputs (negative total balance)
        [Item(n, types[n], ain - aout) for n, (ain, aout) in items.items()
            if not np.isclose(ain, aout) and ain > aout],
        # Intermediate (there is both consumption and production)
        [Item(n, types[n], max(ain, aout)) for n, (ain, aout) in items.items()
            if not np.isclose(ain, 0) and not np.isclose(aout, 0)],
        # Outputs (positive total balance)
        [Item(n, types[n], aout - ain) for n, (ain, aout) in items.items()
            if not np.isclose(ain, aout) and aout > ain]
    )


def optimize(objectives, resources, technologies, weights=None):
    """Find optimal production inputs and respective technologies."""
    if weights is None:
        weights = default_weights(resources)
    technologies = enumerate_items(technologies)
    products = list(list_items(technologies) - resources)
    product_id = {p: i for i, p in enumerate(products)}
    no_vars = sum(len(t.inputs) + len(t.outputs) for t in technologies)

    # Preapare and solve LP problem
    # (method='interior-point' fails to find some solutions)
    A_eq, b_eq = eq_matrices(technologies, no_vars)
    A_ub, b_ub = ub_matrices(technologies, product_id, objectives, no_vars)
    c = obj_vector(technologies, weights, no_vars)
    lp_res = linprog(c, A_ub, b_ub, A_eq, b_eq, method='highs-ds')
    if not lp_res.success:
        raise RuntimeError("The linear programming problem has no solution.")

    solution = collect_results(technologies, lp_res)
    return solution, aggregate_flows(solution)


def optimize_or(objectives, resources, technologies):
    """Compute optimal technologes that would satisfy either objective."""
    solutions = [optimize({k: v}, resources, technologies)
        for k, v in objectives.items()]

    # Merge technologies
    sol = [t for s, _ in solutions for t in s]
    key = lambda t: t.name
    sol = [list(g) for n, g in groupby(sorted(sol, key=key), key=key)]
    sol = [OptimalTech(**update(g[0], cycles=max(t.cycles for t in g))) for g in sol]

    # Merge flows
    def merge_flow(k):
        items = [i for _, f in solutions for i in f[k]]
        key = lambda i: i.name
        items = [list(g) for n, g in groupby(sorted(items, key=key), key=key)]
        return [Item(*g[0][:2], max(t[2] for t in g)) for g in items]

    flows = TotalFlows(*(merge_flow(i) for i in range(3)))
    return sol, flows
