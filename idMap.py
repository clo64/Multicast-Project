#100-199 Hosts
#200-254 Routers
def code_to_IP(code):
    switcher={
        101:'192.168.1.101',
        201:'192.168.1.201',
        203: '192.168.1.203'
    }
    return switcher.get(code, "Invalid Code")