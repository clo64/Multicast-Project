#100-199 Hosts
#200-254 Routers
def code_to_IP(code):
    switcher={
        100:'192.168.1.1',
        200:'192.168.2.1'
    }
    return switcher.get(code, "Invalid Code")