"""Unit definitions, exact by definition, so a value a source states in inches or pounds
is converted once, here, and stored in the knowledge base in the SI units the rules use:
mm, kg, N, MPa (N/mm2), kg/m3.

The international yard and pound agreement (1959) defines the inch as 25.4 mm and the
pound as 0.45359237 kg; standard gravity is 9.80665 m/s2 by the CGPM's 1901 definition.
"""

INCH_MM = 25.4
FOOT_MM = 12 * INCH_MM
POUND_KG = 0.45359237
CUBIC_FOOT_MM3 = FOOT_MM ** 3
POUND_PER_CUBIC_FOOT_KG_M3 = POUND_KG / (FOOT_MM / 1000) ** 3
STANDARD_GRAVITY = 9.80665  # m/s2; a mass in kg times this is a force in N
POUND_FORCE_N = POUND_KG * STANDARD_GRAVITY  # the pound-force: a pound's weight under standard gravity
SQUARE_FOOT_M2 = (FOOT_MM / 1000) ** 2
POUND_PER_SQUARE_FOOT_KG_M2 = POUND_KG / SQUARE_FOOT_M2  # a surface load, lb/ft2, as kg/m2
POUND_PER_FOOT_KG_M = POUND_KG / (FOOT_MM / 1000)  # a load along a length, lb/ft, as kg/m
