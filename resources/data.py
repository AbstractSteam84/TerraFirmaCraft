#  Work under Copyright. Licensed under the EUPL.
#  See the project README.md and LICENSE.txt for more information.

from enum import Enum, auto

from mcresources import ResourceManager, utils
from mcresources.utils import item_stack

from constants import *


class Size(Enum):
    tiny = auto()
    very_small = auto()
    small = auto()
    normal = auto()
    large = auto()
    very_large = auto()
    huge = auto()


class Weight(Enum):
    very_light = auto()
    light = auto()
    medium = auto()
    heavy = auto()
    very_heavy = auto()


class Category(Enum):
    fruit = auto()
    vegetable = auto()
    grain = auto()
    bread = auto()
    dairy = auto()
    meat = auto()
    cooked_meat = auto()
    other = auto()


def generate(rm: ResourceManager):
    # Metals
    for metal, metal_data in METALS.items():
        # The metal itself
        rm.data(('tfc', 'metals', metal), {
            'tier': metal_data.tier,
            'fluid': 'tfc:metal/%s' % metal
        })

        # for each registered metal item
        for item, item_data in {**METAL_ITEMS, **METAL_BLOCKS}.items():
            if item_data.type in metal_data.types or item_data.type == 'all':
                if item_data.tag is not None:
                    rm.item_tag(item_data.tag + '/' + metal, 'tfc:metal/%s/%s' % (item, metal))
                    ingredient = item_stack('tag!%s/%s' % (item_data.tag, metal))
                else:
                    ingredient = item_stack('tfc:metal/%s/%s' % (item, metal))
                if item == 'shovel':
                    rm.item_tag('extinguisher', 'tfc:metal/shovel/' + metal)
                elif item == 'knife':
                    rm.item_tag('knives', 'tfc:metal/knife/' + metal)
                elif item == 'saw':
                    rm.item_tag('saws', 'tfc:metal/saw/' + metal)
                elif item == 'chisel':
                    rm.item_tag('chisels', 'tfc:metal/chisel/' + metal)
                elif item == 'hammer':
                    rm.item_tag('hammers', 'tfc:metal/hammer/' + metal)

                metal_item(rm, ('metal', metal + '_' + item), ingredient, 'tfc:%s' % metal, item_data.smelt_amount)
                heat_item(rm, ('metal', metal + '_' + item), ingredient, metal_data.heat_capacity, metal_data.melt_temperature)

        # Common metal crafting tools
        if 'tool' in metal_data.types:
            for tool in ('hammer', 'chisel', 'axe', 'pickaxe', 'shovel'):
                rm.item_tag('tfc:%ss' % tool, 'tfc:metal/%s/%s' % (tool, metal))
            rm.item_tag('forge:shears', 'tfc:metal/shears/%s' % metal)

    # Misc metal items
    metal_item(rm, 'wrought_iron_grill', 'tfc:wrought_iron_grill', 'tfc:cast_iron', 100)

    # Item heat definitions
    heat_item(rm, 'wrought_iron_grill', 'tfc:wrought_iron_grill', 0.35, 1535)
    heat_item(rm, 'stick', 'tag!forge:rods/wooden', 0.3)
    heat_item(rm, 'stick_bunch', 'tfc:stick_bunch', 0.05)
    heat_item(rm, 'glass_shard', 'tfc:glass_shard', 1)
    heat_item(rm, 'sand', 'tag!forge:sand', 0.8)
    heat_item(rm, 'ceramic_unfired_brick', 'tfc:ceramic/unfired_brick', 1)
    heat_item(rm, 'ceramic_unfired_flower_pot', 'tfc:ceramic/unfired_flower_pot', 1)
    heat_item(rm, 'ceramic_unfired_jug', 'tfc:ceramic/unfired_jug', 1)
    heat_item(rm, 'terracotta', ['minecraft:terracotta', *['minecraft:%s_terracotta' % color for color in COLORS]], 0.8)
    heat_item(rm, 'dough', ['tfc:food/%s_dough' % grain for grain in GRAINS], 1)

    for pottery in PAIRED_POTTERY:
        heat_item(rm, 'unfired_' + pottery, 'tfc:ceramic/unfired_' + pottery, 1)

    # Rocks
    for rock, rock_data in ROCKS.items():
        rm.data(('tfc', 'rocks', rock), {
            **dict((block_type, 'tfc:rock/%s/%s' % (block_type, rock)) for block_type in ROCK_BLOCKS_IN_JSON),
            'sand': 'tfc:sand/%s' % rock_data.sand,
            'sandstone': 'tfc:raw_sandstone/%s' % rock_data.sand
        })

        def block(block_type: str):
            return 'tfc:rock/%s/%s' % (block_type, rock)

        rm.block_tag('forge:gravel', block('gravel'))
        rm.block_tag('forge:stone', block('raw'), block('hardened'))
        rm.block_tag('forge:cobblestone', block('cobble'), block('mossy_cobble'))
        rm.block_tag('minecraft:base_stone_overworld', block('raw'), block('hardened'))
        rm.block_tag('forge:stone_bricks', block('bricks'), block('mossy_bricks'), block('cracked_bricks'))
        rm.block_tag('forge:smooth_stone', block('smooth'))
        rm.item_tag('forge:smooth_stone', block('smooth'))
        rm.item_tag('forge:smooth_stone_slab', 'tfc:rock/smooth/%s_slab' % rock)
        rm.block_tag('tfc:breaks_when_isolated', block('raw'))
        rm.item_tag('tfc:rock_knapping', block('loose'))
        rm.item_tag('tfc:%s_rock' % rock_data.category, block('loose'))
        rm.block_tag('minecraft:stone_pressure_plates', block('pressure_plate'))
        rm.item_tag('minecraft:stone_pressure_plates', block('pressure_plate'))

        if rock in ['chalk', 'dolomite', 'limestone', 'marble']:
            rm.item_tag('tfc:fluxstone', block('loose'))
    rm.block_tag('tfc:forge_insulation', '#forge:stone', '#forge:cobblestone', '#forge:stone_bricks', '#forge:smooth_stone')

    for category in ROCK_CATEGORIES:
        rm.item_tag('tfc:knives', 'tfc:stone/knife/%s' % category)

    rm.item_tag('tfc:clay_knapping', 'minecraft:clay_ball')
    rm.item_tag('tfc:fire_clay_knapping', 'tfc:fire_clay')
    rm.item_tag('tfc:leather_knapping', 'minecraft:leather')
    rm.item_tag('tfc:knapping_any', '#tfc:clay_knapping', '#tfc:fire_clay_knapping', '#tfc:leather_knapping', '#tfc:rock_knapping')

    # Plants
    for plant, plant_data in PLANTS.items():
        rm.block_tag('plant', 'tfc:plant/%s' % plant)
        if plant_data.type in {'standard', 'short_grass', 'creeping'}:
            rm.block_tag('can_be_snow_piled', 'tfc:plant/%s' % plant)

    # Sand
    for color in SAND_BLOCK_TYPES:
        rm.block_tag('minecraft:sand', 'tfc:sand/%s' % color)

    for gem in GEMS:
        rm.item_tag('forge:gems', 'tfc:gem/' + gem)
    rm.item_tag('forge:gems/diamond', 'tfc:gem/diamond')
    rm.item_tag('forge:gems/lapis', 'tfc:gem/lapis_lazuli')
    rm.item_tag('forge:gems/emerald', 'tfc:gem/emerald')

    for wood in WOODS:
        rm.data(('tfc', 'supports', wood), {
            'ingredient': 'tfc:wood/horizontal_support/%s' % wood,
            'support_up': 1,
            'support_down': 1,
            'support_horizontal': 4
        })

    # Forge you dingus, use vanilla tags
    rm.block_tag('forge:sand', '#minecraft:sand')

    for wood, wood_data in WOODS.items():
        rm.item_tag('minecraft:logs', 'tfc:wood/log/%s' % wood)
        rm.item_tag('minecraft:logs', 'tfc:wood/wood/%s' % wood)
        rm.item_tag('forge:rods/wooden',  'tfc:wood/twig/%s' % wood)
        rm.block_tag('lit_by_dropped_torch', 'tfc:wood/fallen_leaves/' + wood)
        fuel_item(rm, wood + '_log', 'tfc:wood/log/' + wood, wood_data.duration, wood_data.temp, firepit=True)
        rm.item_tag('lumber', 'tfc:wood/lumber/%s' % wood)

    rm.block_tag('scraping_surface', '#minecraft:logs')
    rm.item_tag('log_pile_logs', 'tfc:stick_bundle')
    rm.item_tag('pit_kiln_straw', 'tfc:straw')
    rm.item_tag('firepit_fuel', '#minecraft:logs')
    rm.item_tag('firepit_logs', '#minecraft:logs')
    rm.item_tag('log_pile_logs', '#minecraft:logs')
    rm.item_tag('pit_kiln_logs', '#minecraft:logs')
    rm.item_tag('can_be_lit_on_torch', '#forge:rods/wooden')

    fuel_item(rm, 'coal', ['minecraft:coal', 'tfc:ore/bituminous_coal'], 2200, 1415)
    fuel_item(rm, 'lignite', 'tfc:ore/lignite', 2200, 1350)
    fuel_item(rm, 'charcoal', 'minecraft:charcoal', 1800, 1350, bloomery=True)
    fuel_item(rm, 'peat', 'tfc:peat', 2500, 600, firepit=True)
    fuel_item(rm, 'stick_bundle', 'tfc:stick_bundle', 600, 900, firepit=True)

    rm.item_tag('minecraft:coals', 'tfc:ore/bituminous_coal', 'tfc:ore/lignite')
    rm.item_tag('forge_fuel', '#minecraft:coals')

    # Tags
    rm.item_tag('forge:ingots/cast_iron', 'minecraft:iron_ingot')
    rm.item_tag('firepit_sticks', '#forge:rods/wooden')
    rm.item_tag('firepit_kindling', 'tfc:straw', 'minecraft:paper', 'minecraft:book', 'tfc:groundcover/pinecone')
    rm.item_tag('starts_fires_with_durability', 'minecraft:flint_and_steel')
    rm.item_tag('starts_fires_with_items', 'minecraft:fire_charge')
    rm.item_tag('handstone', 'tfc:handstone')
    rm.item_tag('high_quality_cloth', 'tfc:silk_cloth', 'tfc:wool_cloth')
    rm.item_tag('minecraft:stone_pressure_plates', 'minecraft:stone_pressure_plate', 'minecraft:polished_blackstone_pressure_plate')

    rm.block_tag('tree_grows_on', 'minecraft:grass_block', '#forge:dirt', '#tfc:grass')
    rm.block_tag('supports_landslide', 'minecraft:grass_path')
    rm.block_tag('bush_plantable_on', 'minecraft:grass_block', '#forge:dirt', '#tfc:grass')
    rm.block_tag('small_spike', 'tfc:calcite')
    rm.block_tag('sea_bush_plantable_on', '#forge:dirt', '#minecraft:sand', '#forge:gravel')
    rm.block_tag('creeping_plantable_on', 'minecraft:grass_block', '#tfc:grass', '#minecraft:base_stone_overworld', '#minecraft:logs')
    rm.block_tag('minecraft:bamboo_plantable_on', '#tfc:grass')
    rm.block_tag('minecraft:climbable', 'tfc:plant/hanging_vines', 'tfc:plant/hanging_vines_plant', 'tfc:plant/liana', 'tfc:plant/liana_plant')
    rm.block_tag('kelp_tree', 'tfc:plant/giant_kelp_flower', 'tfc:plant/giant_kelp_plant')
    rm.block_tag('kelp_flower', 'tfc:plant/giant_kelp_flower')
    rm.block_tag('kelp_branch', 'tfc:plant/giant_kelp_plant')
    rm.block_tag('lit_by_dropped_torch', 'tfc:log_pile', 'tfc:thatch', 'tfc:pit_kiln')
    rm.block_tag('charcoal_cover_whitelist', 'tfc:log_pile', 'tfc:charcoal_pile', 'tfc:burning_log_pile')
    rm.block_tag('forge_invisible_whitelist', 'minecraft:glass')  # todo: set this to just be crucibles
    rm.block_tag('any_spreading_bush', '#tfc:spreading_bush')

    # Thatch Bed
    rm.item_tag('thatch_bed_hides', 'tfc:large_raw_hide', 'tfc:large_sheepskin_hide')
    rm.block_tag('thatch_bed_thatch', 'tfc:thatch')
    rm.item_tag('scrapable', 'tfc:large_soaked_hide', 'tfc:medium_soaked_hide', 'tfc:small_soaked_hide')

    # Misc
    rm.item_tag('mortar', 'tfc:mortar')

    # Fluids
    rm.fluid_tag('usable_in_pot', '#tfc:fluid_ingredients')
    rm.fluid_tag('fluid_ingredients', 'minecraft:water', 'tfc:salt_water', 'tfc:spring_water')

    for mat in VANILLA_TOOL_MATERIALS:
        rm.item_tag('extinguisher', 'minecraft:' + mat + '_shovel')

    # Plants
    for plant in PLANTS.keys():
        rm.block_tag('can_be_snow_piled', 'tfc:plant/%s' % plant)

    rm.block_tag('snow', 'minecraft:snow', 'minecraft:snow_block', 'tfc:snow_pile')

    # Valid spawn tag - grass, sand, or raw rock
    rm.block_tag('minecraft:valid_spawn', *['tfc:grass/%s' % v for v in SOIL_BLOCK_VARIANTS], *['tfc:sand/%s' % c for c in SAND_BLOCK_TYPES], *['tfc:rock/raw/%s' % r for r in ROCKS.keys()])
    rm.block_tag('forge:dirt', *['tfc:dirt/%s' % v for v in SOIL_BLOCK_VARIANTS])

    # todo: specific item size definitions for a whole bunch of items that aren't naturally assigned
    item_size(rm, 'logs', 'tag!minecraft:logs', Size.very_large, Weight.medium)

    # Food
    food_item(rm, 'banana', 'tfc:food/banana', Category.fruit, 4, 0.2, 0, 2, fruit=1)
    food_item(rm, 'blackberry', 'tfc:food/blackberry', Category.fruit, 4, 0.2, 5, 4.9, fruit=0.75)
    food_item(rm, 'blueberry', 'tfc:food/blueberry', Category.fruit, 4, 0.2, 5, 4.9, fruit=0.75)
    food_item(rm, 'bunchberry', 'tfc:food/bunchberry', Category.fruit, 4, 0.5, 5, 4.9, fruit=0.75)
    food_item(rm, 'cherry', 'tfc:food/cherry', Category.fruit, 4, 0.2, 5, 4, fruit=1)
    food_item(rm, 'cloudberry', 'tfc:food/cloudberry', Category.fruit, 4, 0.5, 5, 4.9, fruit=0.75)
    food_item(rm, 'cranberry', 'tfc:food/cranberry', Category.fruit, 4, 0.2, 5, 1.8, fruit=1)
    food_item(rm, 'elderberry', 'tfc:food/elderberry', Category.fruit, 4, 0.2, 5, 4.9, fruit=1)
    food_item(rm, 'gooseberry', 'tfc:food/gooseberry', Category.fruit, 4, 0.5, 5, 4.9, fruit=0.75)
    food_item(rm, 'green_apple', 'tfc:food/green_apple', Category.fruit, 4, 0.5, 0, 2.5, fruit=1)
    food_item(rm, 'lemon', 'tfc:food/lemon', Category.fruit, 4, 0.2, 5, 2, fruit=0.75)
    food_item(rm, 'olive', 'tfc:food/olive', Category.fruit, 4, 0.2, 0, 1.6, fruit=1)
    food_item(rm, 'orange', 'tfc:food/orange', Category.fruit, 4, 0.5, 10, 2.2, fruit=0.5)
    food_item(rm, 'peach', 'tfc:food/peach', Category.fruit, 4, 0.5, 10, 2.8, fruit=0.5)
    food_item(rm, 'plum', 'tfc:food/plum', Category.fruit, 4, 0.5, 5, 2.8, fruit=0.75)
    food_item(rm, 'raspberry', 'tfc:food/raspberry', Category.fruit, 4, 0.5, 5, 4.9, fruit=0.75)
    food_item(rm, 'red_apple', 'tfc:food/red_apple', Category.fruit, 4, 0.5, 0, 1.7, fruit=1)
    food_item(rm, 'snowberry', 'tfc:food/snowberry', Category.fruit, 4, 0.2, 5, 4.9, fruit=1)
    food_item(rm, 'strawberry', 'tfc:food/strawberry', Category.fruit, 4, 0.5, 10, 4.9, fruit=0.5)
    food_item(rm, 'wintergreen_berry', 'tfc:food/wintergreen_berry', Category.fruit, 4, 0.2, 5, 4.9, fruit=1)
    food_item(rm, 'barley', 'tfc:food/barley', Category.grain, 4, 0, 0, 2)
    food_item(rm, 'barley_grain', 'tfc:food/barley_grain', Category.grain, 4, 0, 0, 0.25)
    food_item(rm, 'barley_flour', 'tfc:food/barley_flour', Category.grain, 4, 0, 0, 0.5)
    food_item(rm, 'barley_dough', 'tfc:food/barley_dough', Category.grain, 4, 0, 0, 3)
    food_item(rm, 'barley_bread', 'tfc:food/barley_bread', Category.bread, 4, 1, 0, 1, grain=1.5)
    food_item(rm, 'maize', 'tfc:food/maize', Category.grain, 4, 0, 0, 2)
    food_item(rm, 'maize_grain', 'tfc:food/maize_grain', Category.grain, 4, 0.5, 0, 0.25)
    food_item(rm, 'maize_flour', 'tfc:food/maize_flour', Category.grain, 4, 0, 0, 0.5)
    food_item(rm, 'maize_dough', 'tfc:food/maize_dough', Category.grain, 4, 0, 0, 3)
    food_item(rm, 'maize_bread', 'tfc:food/maize_bread', Category.bread, 4, 1, 0, 1, grain=1)
    food_item(rm, 'oat', 'tfc:food/oat', Category.grain, 4, 0, 0, 2)
    food_item(rm, 'oat_grain', 'tfc:food/oat_grain', Category.grain, 4, 0.5, 0, 0.25)
    food_item(rm, 'oat_flour', 'tfc:food/oat_flour', Category.grain, 4, 0, 0, 0.5)
    food_item(rm, 'oat_dough', 'tfc:food/oat_dough', Category.grain, 4, 0, 0, 3)
    food_item(rm, 'oat_bread', 'tfc:food/oat_bread', Category.bread, 4, 1, 0, 1, grain=1)
    # todo: figure out what to do with rice. thinking rice -> grain -> cooked rice in a pot recipe? so remove flour/dough/bread for this one
    food_item(rm, 'rice', 'tfc:food/rice', Category.grain, 4, 0, 0, 2)
    food_item(rm, 'rice_grain', 'tfc:food/rice_grain', Category.grain, 4, 0.5, 0, 0.25)
    food_item(rm, 'rice_flour', 'tfc:food/rice_flour', Category.grain, 4, 0, 0, 0.5)
    food_item(rm, 'rice_dough', 'tfc:food/rice_dough', Category.grain, 4, 0, 0, 3)
    food_item(rm, 'rice_bread', 'tfc:food/rice_bread', Category.bread, 4, 1, 0, 1, grain=1.5)
    food_item(rm, 'rye', 'tfc:food/rye', Category.grain, 4, 0, 0, 2)
    food_item(rm, 'rye_grain', 'tfc:food/rye_grain', Category.grain, 4, 0.5, 0, 0.25)
    food_item(rm, 'rye_flour', 'tfc:food/rye_flour', Category.grain, 4, 0, 0, 0.5)
    food_item(rm, 'rye_dough', 'tfc:food/rye_dough', Category.grain, 4, 0, 0, 3)
    food_item(rm, 'rye_bread', 'tfc:food/rye_bread', Category.bread, 4, 1, 0, 1, grain=1.5)
    food_item(rm, 'wheat', 'tfc:food/wheat', Category.grain, 4, 0, 0, 2)
    food_item(rm, 'wheat_grain', 'tfc:food/wheat_grain', Category.grain, 4, 0.5, 0, 0.25)
    food_item(rm, 'wheat_flour', 'tfc:food/wheat_flour', Category.grain, 4, 0, 0, 0.5)
    food_item(rm, 'wheat_dough', 'tfc:food/wheat_dough', Category.grain, 4, 0, 0, 3)
    food_item(rm, 'wheat_bread', 'tfc:food/wheat_bread', Category.bread, 4, 1, 0, 1, grain=1)
    food_item(rm, 'beet', 'tfc:food/beet', Category.vegetable, 4, 2, 0, 0.7, veg=1)
    food_item(rm, 'cabbage', 'tfc:food/cabbage', Category.vegetable, 4, 0.5, 0, 1.2, veg=1)
    food_item(rm, 'carrot', 'tfc:food/carrot', Category.vegetable, 4, 2, 0, 0.7, veg=1)
    food_item(rm, 'garlic', 'tfc:food/garlic', Category.vegetable, 4, 0.5, 0, 0.4, veg=2)
    food_item(rm, 'green_bean', 'tfc:food/green_bean', Category.vegetable, 4, 0.5, 0, 3.5, veg=1)
    food_item(rm, 'green_bell_pepper', 'tfc:food/green_bell_pepper', Category.vegetable, 4, 0.5, 0, 2.7, veg=1)
    food_item(rm, 'onion', 'tfc:food/onion', Category.vegetable, 4, 0.5, 0, 0.5, veg=1)
    food_item(rm, 'potato', 'tfc:food/potato', Category.vegetable, 4, 2, 0, 0.666, veg=1.5)
    food_item(rm, 'red_bell_pepper', 'tfc:food/red_bell_pepper', Category.vegetable, 4, 1, 0, 2.5, veg=1)
    # todo: proper foods for our different sea plants that are harvestable?
    # food_item(rm, 'seaweed', 'tfc:food/seaweed', Category.vegetable, 4, 1, 0, 2.5, veg=1)
    food_item(rm, 'soybean', 'tfc:food/soybean', Category.vegetable, 4, 2, 0, 2.5, veg=0.5, protein=1)
    food_item(rm, 'squash', 'tfc:food/squash', Category.vegetable, 4, 1, 0, 1.67, veg=1.5)
    food_item(rm, 'tomato', 'tfc:food/tomato', Category.vegetable, 4, 0.5, 5, 3.5, veg=1.5)
    food_item(rm, 'yellow_bell_pepper', 'tfc:food/yellow_bell_pepper', Category.vegetable, 4, 1, 0, 2.5, veg=1)
    food_item(rm, 'cheese', 'tfc:food/cheese', Category.dairy, 4, 2, 0, 0.3, dairy=3)
    food_item(rm, 'cooked_egg', 'tfc:food/cooked_egg', Category.other, 4, 0.5, 0, 4, protein=0.75, dairy=0.25)
    # todo: figure out what to do with sugarcane, do we need a different plant? or item or something? or modify the vanilla one
    # food_item(rm, 'sugarcane', 'tfc:food/sugarcane', Category.grain, 4, 0, 0, 1.6, grain=0.5)
    food_item(rm, 'beef', 'tfc:food/beef', Category.meat, 4, 0, 0, 2, protein=2)
    food_item(rm, 'pork', 'tfc:food/pork', Category.meat, 4, 0, 0, 2, protein=1.5)
    food_item(rm, 'chicken', 'tfc:food/chicken', Category.meat, 4, 0, 0, 3, protein=1.5)
    food_item(rm, 'mutton', 'tfc:food/mutton', Category.meat, 4, 0, 0, 3, protein=1.5)
    # todo: different fish types?
    # food_item(rm, 'fish', 'tfc:food/fish', Category.meat, 4, 0, 0, 3, protein=1)
    food_item(rm, 'bear', 'tfc:food/bear', Category.meat, 4, 0, 0, 2, protein=1.5)
    # food_item(rm, 'calamari', 'tfc:food/calamari', Category.meat, 4, 0, 0, 3, protein=0.5)
    food_item(rm, 'horse_meat', 'tfc:food/horse_meat', Category.meat, 4, 0, 0, 2, protein=1.5)
    food_item(rm, 'pheasant', 'tfc:food/pheasant', Category.meat, 4, 0, 0, 3, protein=1.5)
    food_item(rm, 'venison', 'tfc:food/venison', Category.meat, 4, 0, 0, 2, protein=1)
    food_item(rm, 'wolf', 'tfc:food/wolf', Category.meat, 4, 0, 0, 3, protein=0.5)
    food_item(rm, 'rabbit', 'tfc:food/rabbit', Category.meat, 4, 0, 0, 3, protein=0.5)
    food_item(rm, 'hyena', 'tfc:food/hyena', Category.meat, 4, 0, 0, 3, protein=0.5)
    food_item(rm, 'duck', 'tfc:food/duck', Category.meat, 4, 0, 0, 3, protein=0.5)
    food_item(rm, 'chevon', 'tfc:food/chevon', Category.meat, 4, 0, 0, 3, protein=0.5)
    food_item(rm, 'gran_feline', 'tfc:food/gran_feline', Category.meat, 4, 0, 0, 3, protein=0.5)
    food_item(rm, 'camelidae', 'tfc:food/camelidae', Category.meat, 4, 0, 0, 3, protein=0.5)
    food_item(rm, 'cooked_beef', 'tfc:food/cooked_beef', Category.cooked_meat, 4, 2, 0, 1.5, protein=2.5)
    food_item(rm, 'cooked_pork', 'tfc:food/cooked_pork', Category.cooked_meat, 4, 2, 0, 1.5, protein=2.5)
    food_item(rm, 'cooked_chicken', 'tfc:food/cooked_chicken', Category.cooked_meat, 4, 2, 0, 2.25, protein=2.5)
    food_item(rm, 'cooked_mutton', 'tfc:food/cooked_mutton', Category.cooked_meat, 4, 2, 0, 2.25, protein=2.5)
    # todo: see fish note above
    # food_item(rm, 'cooked_fish', 'tfc:food/cooked_fish', Category.cooked_meat, 4, 1, 0, 2.25, protein=2)
    food_item(rm, 'cooked_bear', 'tfc:food/cooked_bear', Category.cooked_meat, 4, 1, 0, 1.5, protein=2.5)
    # food_item(rm, 'cooked_calamari', 'tfc:food/cooked_calamari', Category.cooked_meat, 4, 1, 0, 2.25, protein=1.5)
    food_item(rm, 'cooked_horse_meat', 'tfc:food/cooked_horse_meat', Category.cooked_meat, 4, 2, 0, 1.5, protein=2.5)
    food_item(rm, 'cooked_pheasant', 'tfc:food/cooked_pheasant', Category.cooked_meat, 4, 1, 0, 2.25, protein=2.5)
    food_item(rm, 'cooked_venison', 'tfc:food/cooked_venison', Category.cooked_meat, 4, 1, 0, 1.5, protein=2)
    food_item(rm, 'cooked_wolf', 'tfc:food/cooked_wolf', Category.cooked_meat, 4, 1, 0, 2.25, protein=1.5)
    food_item(rm, 'cooked_rabbit', 'tfc:food/cooked_rabbit', Category.cooked_meat, 4, 1, 0, 2.25, protein=1.5)
    food_item(rm, 'cooked_hyena', 'tfc:food/cooked_hyena', Category.cooked_meat, 4, 1, 0, 2.25, protein=1.5)
    food_item(rm, 'cooked_duck', 'tfc:food/cooked_duck', Category.cooked_meat, 4, 1, 0, 2.25, protein=1.5)
    food_item(rm, 'cooked_chevon', 'tfc:food/cooked_chevon', Category.cooked_meat, 4, 1, 0, 2.25, protein=2)
    food_item(rm, 'cooked_gran_feline', 'tfc:food/cooked_gran_feline', Category.cooked_meat, 4, 2, 0, 2.25, protein=2.5)
    food_item(rm, 'cooked_camelidae', 'tfc:food/cooked_camelidae', Category.cooked_meat, 4, 2, 0, 2.25, protein=2.5)


def food_item(rm: ResourceManager, name_parts: utils.ResourceIdentifier, ingredient: utils.Json, category: Category, hunger: int, saturation: float, water: int, decay: float, fruit: Optional[float] = None, veg: Optional[float] = None, protein: Optional[float] = None, grain: Optional[float] = None, dairy: Optional[float] = None):
    rm.data(('tfc', 'food_items', name_parts), {
        'ingredient': utils.ingredient(ingredient),
        'category': category.name,
        'hunger': hunger,
        'saturation': saturation,
        'water': water if water != 0 else None,
        'decay': decay,
        'fruit': fruit,
        'vegetables': veg,
        'protein': protein,
        'grain': grain,
        'dairy': dairy
    })


def item_size(rm: ResourceManager, name_parts: utils.ResourceIdentifier, ingredient: utils.Json, size: Size, weight: Weight):
    rm.data(('tfc', 'item_sizes', name_parts), {
        'ingredient': utils.ingredient(ingredient),
        'size': size.name,
        'weight': weight.name
    })


def metal_item(rm: ResourceManager, name_parts: utils.ResourceIdentifier, ingredient: utils.Json, metal: str, amount: int):
    rm.data(('tfc', 'metal_items', name_parts), {
        'ingredient': utils.ingredient(ingredient),
        'metal': metal,
        'amount': amount
    })


def heat_item(rm: ResourceManager, name_parts: utils.ResourceIdentifier, ingredient: utils.Json, heat_capacity: float, melt_temperature: Optional[int] = None):
    if melt_temperature is not None:
        forging_temperature = melt_temperature * 0.6
        welding_temperature = melt_temperature * 0.8
    else:
        forging_temperature = welding_temperature = None
    rm.data(('tfc', 'item_heats', name_parts), {
        'ingredient': utils.ingredient(ingredient),
        'heat_capacity': heat_capacity,
        'forging_temperature': forging_temperature,
        'welding_temperature': welding_temperature
    })


def fuel_item(rm: ResourceManager, name_parts: utils.ResourceIdentifier, ingredient: utils.Json, duration: int, temperature: float, forge: bool = False, bloomery: bool = False, firepit: bool = False):
    if forge:
        rm.item_tag('forge_fuel', ingredient)
    if bloomery:
        rm.item_tag('bloomery_fuel', ingredient)
    if firepit:
        rm.item_tag('firepit_fuel', ingredient)
    rm.data(('tfc', 'fuels', name_parts), {
        'ingredient': utils.ingredient(ingredient),
        'duration': duration,
        'temperature': temperature
    })
