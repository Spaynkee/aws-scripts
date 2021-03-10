from CHDelete import CHDelete

if __name__ == "__main__":
    chd = CHDelete()
    chd.destroy_role("web-serv-role")
    chd.destroy_instance_key_pair("web-serv-keypair")
    chd.destroy_instance_profile("web-serv-prof")
    chd.destroy_instance("WebServ")
    chd.destroy_security_group("web-serv-sg")
