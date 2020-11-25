import sympy as sp

"""
System:
                           ^
                           | PowerOut
                           |
                           |
               +-----------+------------+
               |                        |
               |                        |
+------------->+                        |
               |          Box           |
  PowerIn      |                        |
               |                        |
               |                        |
               +------------------------+

"""

if __name__ == '__main__':
    P_in = sp.symbols("P_in")
    P_out = sp.symbols("P_out")
    P_total = sp.symbols("P_total")

    m_air = sp.symbols("m_air")
    c_air = sp.symbols("c_air")  # Specific heat capacity

    C_air = m_air * c_air

    dT_dt = 1 / C_air * (P_in - P_out)
    print(f"dT_dt = {dT_dt}")

    V_heater = sp.symbols("V_heater")  # Voltage of heater
    i_heater = sp.symbols("i_heater")  # Current of heater

    P_in_num = V_heater * i_heater  # Electrical power in

    G_out = sp.symbols("G_out") # Coefficient of heat transfer through the styrofoam box.
    T = sp.symbols("T")  # Temperature in the box
    T_room = sp.symbols("T_room")  # Temperature in the room

    P_out_num = G_out * (T - T_room)

    dT_dt = dT_dt.subs(P_in, P_in_num).subs(P_out, P_out_num)

    print(f"dT_dt = {dT_dt}")