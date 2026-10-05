#!/usr/bin/env python3
import os
OUT = os.path.expanduser('~/virtual-autonomous-warehouse/src/warehouse_gazebo/worlds/warehouse.sdf')
models = []

def add(name, x, y, z, geom, color, collide=True):
    c = '<collision name="c"><geometry>%s</geometry></collision>' % geom if collide else ''
    m = '<material><ambient>%s</ambient><diffuse>%s</diffuse></material>' % (color, color)
    models.append('    <model name="%s"><static>true</static><pose>%s %s %s 0 0 0</pose>'
                  '<link name="l">%s<visual name="v"><geometry>%s</geometry>%s</visual></link></model>'
                  % (name, x, y, z, c, geom, m))

def box(name, x, y, z, sx, sy, sz, color, collide=True):
    add(name, x, y, z, '<box><size>%s %s %s</size></box>' % (sx, sy, sz), color, collide)

def cyl(name, x, y, z, r, l, color):
    add(name, x, y, z, '<cylinder><radius>%s</radius><length>%s</length></cylinder>' % (r, l), color)

WALL, SHELF, CRATE, PALLET = '0.8 0.8 0.8 1', '0.55 0.35 0.1 1', '0.75 0.55 0.25 1', '0.6 0.45 0.25 1'

# floor and walls (20 x 20)
box('floor', 0, 0, -0.05, 20, 20, 0.1, '0.6 0.6 0.6 1')
box('wall_n', 0, 10, 1, 20, 0.2, 2, WALL)
box('wall_s', 0, -10, 1, 20, 0.2, 2, WALL)
box('wall_e', 10, 0, 1, 0.2, 20, 2, WALL)
box('wall_w', -10, 0, 1, 0.2, 20, 2, WALL)

# shelf rows with stock crates on top
for i, x in enumerate((-7, -4, -1)):
    box('shelf_%d' % (i + 1), x, 2, 1, 0.8, 5, 2, SHELF)
    box('shelf_%d' % (i + 4), x, 7.5, 1, 0.8, 3, 2, SHELF)
    box('stock_a%d' % (i + 1), x, 1, 2.25, 0.5, 0.5, 0.5, CRATE)
    box('stock_b%d' % (i + 1), x, 3.2, 2.25, 0.5, 0.5, 0.5, CRATE)
    box('stock_c%d' % (i + 1), x, 7.5, 2.25, 0.5, 0.5, 0.5, CRATE)

# loading dock (green) with pallets and crates
box('loading_pad', 7, -7, 0.01, 3.6, 3, 0.02, '0.1 0.7 0.2 1', False)
for i, x in enumerate((6.0, 8.0)):
    box('pallet_%d' % (i + 1), x, -7.5, 0.075, 1.2, 1.2, 0.15, PALLET)
    box('load_%d' % (i + 1), x, -7.5, 0.45, 0.6, 0.6, 0.6, CRATE)
    box('load_top_%d' % (i + 1), x, -7.5, 1.0, 0.5, 0.5, 0.5, CRATE)

# unloading / shipping dock (red) with outbound crates
box('shipping_pad', 7, 7, 0.01, 3.6, 3, 0.02, '0.8 0.15 0.15 1', False)
for i, (x, y) in enumerate(((6.5, 7.5), (7.5, 7.5), (7.0, 8.4))):
    box('outbound_%d' % (i + 1), x, y, 0.3, 0.6, 0.6, 0.6, CRATE)

# packing stations along the east wall
box('packing_1', 8.8, -2, 0.45, 1.0, 2.5, 0.9, '0.3 0.3 0.45 1')
box('packing_2', 8.8, 2, 0.45, 1.0, 2.5, 0.9, '0.3 0.3 0.45 1')

# sorting zone (purple)
box('sorting_pad', 4, 3, 0.01, 3, 3, 0.02, '0.5 0.2 0.7 1', False)
box('sort_table', 4, 3, 0.4, 1.2, 0.8, 0.8, '0.35 0.35 0.4 1')

# charging pads (yellow), one behind each parking spot
for i, x in enumerate((-3, -1.5, 0, 1.5, 3)):
    box('charger_%d' % (i + 1), x, -8.5, 0.01, 0.8, 0.8, 0.02, '0.95 0.85 0.1 1', False)

# barrels and cones
for i, y in enumerate((-3.0, -2.2, -1.4)):
    cyl('barrel_%d' % (i + 1), -9, y, 0.4, 0.3, 0.8, '0.2 0.4 0.8 1')
for i, (x, y) in enumerate(((-5, -5.5), (5, -5.5), (-9, 9), (0, 9))):
    cyl('cone_%d' % (i + 1), x, y, 0.2, 0.15, 0.4, '1 0.5 0 1')

world = '''<?xml version="1.0"?>
<sdf version="1.8">
  <world name="default">
    <physics name="1ms" type="ignored"><max_step_size>0.001</max_step_size><real_time_factor>1.0</real_time_factor></physics>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows><pose>0 0 10 0 0 0</pose>
      <diffuse>0.9 0.9 0.9 1</diffuse><specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
%s
  </world>
</sdf>
''' % '\n'.join(models)

with open(OUT, 'w') as f:
    f.write(world)
print('Wrote %d objects to %s' % (len(models), OUT))
