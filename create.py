from CHCreate import CHCreate

if __name__ == "__main__":
    chc = CHCreate()
    chc.create_role("web-serv-role")
    chc.create_instance_key_pair("web-serv-keypair")

    chc.create_security_group("web-serv-sg", "for the web server")
    chc.allow_port_security_group("web-serv-sg", 22)
    chc.allow_port_security_group("web-serv-sg", 80)

    chc.create_instance_profile("web-serv-prof")
    chc.create_instance("web-serv-keypair", "web-serv-prof", "WebServ", "web-serv-sg",\
            "web-server.sh")

