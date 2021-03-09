from CHCreate import CHCreate

if __name__ == "__main__":
    chc = CHCreate()
    chc.create_role("web-serv-role")
    chc.create_instance_key_pair("web-serv-keypair")
    chc.create_instance_profile("web-serv-prof")
    chc.create_instance("web-serv-keypair", "web-serv-prof", "WebServ", "web-server.sh")

