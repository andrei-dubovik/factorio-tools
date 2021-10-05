# Factorio Tools

A personal collection of tools to optimize Factorio bases.

At the moment, I've only programmed the computation of optimal ratios. The
computation works in general, also with recipes that have multiple outputs, or
where multiple recipes are available for the same output (linear programming is
used here). I've also dreamed of computing optimal layouts but that's a more
difficult problem. One day, maybe.

## Setup

Before using the tools, we need to convert Factorio recipes data to .json. This
part is programmed in Lua.

```
lua convert.lua ~/.local/share/Steam/steamapps/common/Factorio/ > recipes.json
```

(The argument to `convert.lua` is the path to the Factorio installation.)

The remaining tools are in Python. The following snippet will load the
functions used in the examples below.

```python
from recipes import load_recipes
from transform import adjust
from production import list_resources, optimize, optimize_or
from interface import print_technologies, print_flows, print_io
```

## Examples

### An Electronics Factory

After loading the libraries, we can load the recipes. Either "normal" or
"expensive" recipes can be loaded.

```python
technologies = load_recipes('recipes.json', mode='normal')
```

By default, the recipes are loaded with crafting speed 1. Suppose we are
currently using Assembling Machine 2 and an Electric Furnace, without any
modules. We can transform the crafting speeds accordingly:

```python
technologies = adjust(technologies, speed={
    'crafting': 0.75,
    'smelting': 2,
})
```

Available categories are: "centrifuging", "chemistry", "crafting",
"oil-processing", "rocket-building", "smelting".

When running the optimizer, an arbitrary list of inputs can be given.  The
optimizer will then minimize the sum of all inputs, using equal weights with
the exception of water, which is given 0 weight (water is cheap and we don't
care how much of it is used.)

First, we load the default inputs (resources):

```python
resources = list_resources(technologies)
```

These are "uranium-ore", "coal", "stone", "copper-ore", "raw-fish",
"crude-oil", "wood", "used-up-uranium-fuel-cell", "water", "steam", "iron-ore".
Suppose we already produce "sulfur", "iron-plate", "copper-plate", and
"plastic-bar" elsewhere and ship them in. We can update the list of resources
accordingly.

```python
resources.update([
    'sulfur', 'iron-plate', 'copper-plate', 'plastic-bar',
])
```

Next, we specify our objective function (units per second). In general,
multiple objectives can be given.

```python
objectives = {'electronic-circuit': 15}
```

Sure, 15 electronic circuits per second is not quite ambitious, but it's a
start. We're ready to run the optimizer now:

```python
solution, flows = optimize(objectives, resources, technologies)
```

A number of convenience functions is proved to pretty-print the optimization
results. These should be reasonably self-explanatory.

```
>>> print_technologies(solution)
name                   cycles/s      cycles    time or count
                      (machine)    (demand)
------------------  -----------  ----------  ---------------
electronic-circuit          1.5        15                 10
copper-cable                1.5        22.5               15

>>> print_flows(flows)
name                    amount  type
--------------------  --------  ------
inputs
  iron-plate              15    item
  copper-plate            22.5  item
intermediate
  copper-cable            45    item
outputs
  electronic-circuit      15    item

>>> print_io(solution)
name                  direction      items/s  type
--------------------  -----------  ---------  ------
electronic-circuit
  iron-plate          in                 1.5  item
  copper-cable        in                 4.5  item
  electronic-circuit  out                1.5  item
copper-cable
  copper-plate        in                 1.5  item
  copper-cable        out                3    item
```

A common design goal I personally faced is to build a factory that can produce
either product A or product B at given throughputs. So, there is a wrapper
around `optimize` to do just that. Say, we want to be able to produce either 15
electronic circuits per second, or 5 advanced circuits, or 0.6 processing
units.

```python
objectives = {
    'electronic-circuit': 15,
    'advanced-circuit': 5,
    'processing-unit': 0.6,
}
solution, flows = optimize_or(objectives, resources, technologies)
```

Let's just take a look at the required machines and the flows.
```
>>> print_technologies(solution)
name                   cycles/s      cycles    time or count
                      (machine)    (demand)
------------------  -----------  ----------  ---------------
advanced-circuit          0.125        5             40
copper-cable              1.5         25             16.6667
electronic-circuit        1.5         15             10
processing-unit           0.075        0.6            8
sulfuric-acid             1            0.06           0.06

>>> print_flows(flows)
name                    amount  type
--------------------  --------  ------
inputs
  copper-plate            25    item
  iron-plate              15    item
  plastic-bar             10    item
  sulfur                   0.3  item
  water                    6    fluid
intermediate
  advanced-circuit         1.2  item
  copper-cable            50    item
  electronic-circuit      14.4  item
  sulfuric-acid            3    fluid
outputs
  advanced-circuit         5    item
  electronic-circuit      15    item
  processing-unit          0.6  item
```

Importantly, the worst possible layout scenario is used when computing flows.
As long as your belts, inserters, etc. satisfy the flows, the factory should be
able to work at capacity.

### A Rocket

Let's build a rocket from scratch. We'll be using Assembling Machines 3 and
Electric Furnaces, without any modules to start with. Regarding the timing, it
could be a rocket per second (default output format), or a rocket per minute,
etc.

```python
technologies = load_recipes('recipes.json', mode='normal')
technologies = adjust(technologies, speed={
    'crafting': 1.25,
    'smelting': 2,
})
resources = list_resources(technologies)
resources.remove('steam')  # don't use steam (steam recipes are currently missing)
objectives = {
    'rocket-silo': 1,
    'rocket-part': 100,
}
solution, flows = optimize(objectives, resources, technologies)
```

Expectedly, advanced oil processing is the way to go:

```
>>> print_technologies(solution)
name                          cycles/s      cycles    time or count
                             (machine)    (demand)
-------------------------  -----------  ----------  ---------------
speed-module                 0.0833333     1000            12000
advanced-oil-processing      0.2           2890.6          14453
heavy-oil-cracking           0.5           1731.62          3463.25
light-oil-cracking           0.5           2400.85          4801.71
sulfuric-acid                1              120              120
plastic-bar                  1             9900             9900
solid-fuel-from-light-oil    0.5          10000            20000
sulfur                       1              300              300
lubricant                    1              300              300
iron-gear-wheel              2.5            200               80
electronic-circuit           2.5          44200            17680
pipe                         2.5            500              200
copper-cable                 2.5          81100            32440
engine-unit                  0.125          200             1600
concrete                     0.125          100              800
copper-plate                 0.625       101100           161760
iron-plate                   0.625        61220            97952
stone-brick                  0.625          500              800
steel-plate                  0.125         3200            25600
advanced-circuit             0.208333      7400            35520
processing-unit              0.125         1200             9600
rocket-silo                  0.0416667        1               24
electric-engine-unit         0.125          200             1600
low-density-structure        0.0625        1000            16000
rocket-fuel                  0.0416667     1000            24000
rocket-control-unit          0.0416667     1000            24000
rocket-part                  0.333333       100              300
```

Here are the total resources used:

```
>>> print_flows(flows)
name                       amount  type
-----------------------  --------  ------
inputs
  water                    299504  fluid
  crude-oil                289060  fluid
  coal                       9900  item
  iron-ore                  61320  item
  copper-ore               101100  item
  stone                      1000  item
intermediate
  ...
```

Let's switch to Productivity Module 3 for all intermediate goods:
```python
technologies = adjust(
    technologies,
    productivity={
        'centrifuging': 1.2,
        'chemistry': 1.3,
        'crafting': 1.4,
        'oil-processing': 1.3,
        'rocket-building': 1.4,
        'smelting': 1.2,
    },
    speed={
        'centrifuging': 0.7,
        'chemistry': 0.55,
        'crafting': 0.4,
        'oil-processing': 0.55,
        'rocket-building': 0.4,
        'smelting': 0.7,
    },
    test=lambda t: t.intermediate,
)
solution, flows = optimize(objectives, resources, technologies)
```

Here are the new total resources:

```
>>> print_flows(flows)
name                        amount  type
-----------------------  ---------  ------
inputs
  water                  79890.6    fluid
  crude-oil              67408.4    fluid
  coal                    2940.28   item
  iron-ore               18636.7    item
  copper-ore             23063.6    item
  stone                    833.333  item
intermediate
  ...
```

Quite a tad more efficient, but those numbers do not account, of course, for
the production of the required productivity modules.

### Electricity from Nuclear

This example is more involved, but it also nicely demonstrates the limitations
of the current scripts. So, essentially no electricity related recipes are
loaded with `load_recipes`. (I didn't yet get around to finding where those
recipes are stored.) Consequently, we need to add a couple of recipes manually
to solve for nuclear steam production.

We start, as before, by loading recipes.

```python
technologies = load_recipes('recipes.json', mode='normal')
```

With benefit of hindsight, we'll need 9 reactors, but that number can be
computed iteratively. Here is the respective neighbour bonus:

```python
# Number of reactors, computed iteratively
n = 9  

# Neighbour bonus, sssuming double-row layout
if n == 1:
    bonus = 0
elif n % 2 == 0:
    bonus = 3 - 4/n
else:
    bonus = 3 - 5/n
```

We can now add technologies for heat, steam, and electricity production.

```python
from recipes import Technology, Item

nuclear_reactor = Technology(
    name = 'operating-nuclear-reactor',
    category = 'electricity-generation',
    intermediate = False,  # not elegible for productivity modules
    inputs = [Item('uranium-fuel-cell', 'item', 1)],
    outputs = [
        Item('used-up-uranium-fuel-cell', 'item', 1),
        Item('heat', 'heat', (bonus + 1)*8000),  # heat energy, MJ
    ],
    time = 200,  # single cycle
)

heat_exchanger = Technology(
    name = 'operating-heat-exchanger',
    category = 'electricity-generation',
    intermediate = False,
    inputs = [
        Item('heat', 'heat', 10),  # heat energy, MJ
        Item('water', 'fluid', 50_000/485),
    ],
    outputs = [Item('steam', 'fluid', 50_000/485)],
    time = 1,
)

steam_turbine = Technology(
    name = 'operating-steam-turbine',
    category = 'electricity-generation',
    intermediate = False,
    inputs = [
        Item('steam', 'fluid', 60),
    ],
    outputs = [Item('electricity', 'electricity', 5.82)],  # MJ
    time = 1,
)

technologies += [nuclear_reactor, heat_exchanger, steam_turbine]
```

Let's use all the latest machines, complete with level 3 productivity modules:

```python
technologies = adjust(technologies, speed={'crafting': 1.25})

technologies = adjust(technologies,
    speed = {'crafting': 0.4, 'centrifuging': 0.6},
    productivity = {'crafting': 1.4, 'centrifuging': 1.2 },
    test = lambda t: t.intermediate,
)
```

We'll assume the iron plates are already produced elsewhere:

```python
resources = list_resources(technologies)
resources.update(['iron-plate'])
```

The objective has been know since 1985:

```python
objectives = {
    'electricity': 1210,
}
```

We're all set now, let's take a look at the solution:

```
>>> solution, flows = optimize(objectives, resources, technologies)
>>> print_technologies(solution)
name                           cycles/s         cycles    time or count
                              (machine)       (demand)
--------------------------  -----------  -------------  ---------------
uranium-processing                0.05     0.0241749          0.483498
kovarex-enrichment-process        0.01     0.000318853        0.0318853
nuclear-fuel-reprocessing         0.01     0.00878226         0.878226
uranium-fuel-cell                 0.05     0.00313652         0.0627304
operating-nuclear-reactor         0.005    0.0439113          8.78226
operating-heat-exchanger          1      121                121
operating-steam-turbine           1      207.904            207.904

>>> print_flows(flows)
name                                amount  type
---------------------------  -------------  -----------
inputs
  uranium-ore                    0.241749   item
  iron-plate                     0.0313652  item
  water                      12474.2        fluid
intermediate
  uranium-235                    0.0158907  item
  uranium-238                    0.0611882  item
  used-up-uranium-fuel-cell      0.0439113  item
  uranium-fuel-cell              0.0439113  item
  heat                        1210          heat
  steam                      12474.2        fluid
outputs
  electricity                 1210          electricity
```

A 1M uranium deposit would allow to generate 1.21 GW of electricity for close
to 48 in-game days (well, slightly less as we can't build precisely 8.78
reactors).  Who needs solar if one has the Kovarex enrichment process?
