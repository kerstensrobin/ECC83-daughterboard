"""
Generate a STEP file for the S9CPC / VTB9-PT 9-pin Noval PCB socket.
Dimensions from VTB9-PT datasheet.
"""
import cadquery as cq
import math

# --- Dimensions (mm) ---
BODY_OD       = 22.8   # main body outer diameter (from cross-section view)
BODY_H        = 5.0    # socket body height above PCB
COLLAR_OD     = 12.0   # top collar outer diameter
COLLAR_H      = 0.5    # top collar height
CENTER_D      = 6.0    # center guide hole diameter
KEY_POST_D    = 3.5    # centre locating/key post diameter
KEY_POST_H    = 0.5    # key post height above collar top

PIN_PCD       = 20.0   # PCB pin pitch circle diameter (matches socket_gzc9-b footprint)
CONTACT_PCD   = 17.5   # contact hole PCD on top face (tube pin circle, B9A standard)
PIN_D         = 1.8    # pin diameter
PIN_TAIL      = 4.5    # pin tail length below PCB (z < 0)
PIN_STUB      = 0.5    # pin stub inside body (z = 0 to PIN_STUB)

CONTACT_D     = 2.0    # socket contact hole diameter (accepts tube pin)
CONTACT_DEPTH = 2.5    # depth of contact hole from top of collar

# 9 pins at 36° spacing; 72° key gap centred at 0° (top)
# pins at 36, 72, 108, 144, 180, 216, 252, 288, 324 degrees
PIN_ANGLES = [36 + i * 36 for i in range(9)]

def cyl(dia, h, x=0, y=0, z=0):
    return (
        cq.Workplane("XY")
        .workplane(offset=z)
        .center(x, y)
        .circle(dia / 2)
        .extrude(h)
    )

# --- Socket body (z=0 .. BODY_H) ---
body = cyl(BODY_OD, BODY_H)

# Collar on top (z=BODY_H .. BODY_H+COLLAR_H)
collar = cyl(COLLAR_OD, COLLAR_H, z=BODY_H)
body = body.union(collar)

# Centre guide hole through entire body+collar
hole = cyl(CENTER_D, BODY_H + COLLAR_H + 1, z=-0.5)
body = body.cut(hole)


# --- Pins ---
r = PIN_PCD / 2

# Socket contact holes on top face (where tube pins insert)
rc = CONTACT_PCD / 2
top_z = BODY_H + COLLAR_H
for deg in PIN_ANGLES:
    rad = math.radians(deg)
    x = rc * math.sin(rad)
    y = rc * math.cos(rad)
    contact_hole = cyl(CONTACT_D, CONTACT_DEPTH, x=x, y=y, z=top_z - CONTACT_DEPTH)
    body = body.cut(contact_hole)
pins = None
for deg in PIN_ANGLES:
    rad = math.radians(deg)
    x = r * math.sin(rad)
    y = r * math.cos(rad)
    # tail below PCB
    tail = cyl(PIN_D, PIN_TAIL, x=x, y=y, z=-PIN_TAIL)
    # stub inside body
    stub = cyl(PIN_D, PIN_STUB, x=x, y=y, z=0)
    pin = tail.union(stub)
    pins = pin if pins is None else pins.union(pin)

result = body.union(pins)

# Gold contact sleeves inside each socket hole (hollow tubes = female receptacles)
CONTACT_WALL = 0.4   # wall thickness of gold sleeve
contacts = None
for deg in PIN_ANGLES:
    rad = math.radians(deg)
    x = rc * math.sin(rad)
    y = rc * math.cos(rad)
    outer = cyl(CONTACT_D, CONTACT_DEPTH, x=x, y=y, z=top_z - CONTACT_DEPTH)
    inner = cyl(CONTACT_D - 2 * CONTACT_WALL, CONTACT_DEPTH, x=x, y=y, z=top_z - CONTACT_DEPTH)
    sleeve = outer.cut(inner)
    contacts = sleeve if contacts is None else contacts.union(sleeve)

assy = cq.Assembly()
assy.add(result, name="socket", color=cq.Color(0.96, 0.92, 0.80))
assy.add(contacts, name="contacts", color=cq.Color(1.0, 0.84, 0.0))

out = "/home/robin/kicad/ECC83-daughterboard/ECC83-daughterboard/S9CPC_VTB9PT.step"
assy.save(out)
print(f"Written: {out}")
