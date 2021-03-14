from CHCreate import CHCreate
import time

if __name__ == "__main__":
    chc = CHCreate()
    chc.create_role("web-serv-role", "instance-role.json")
    chc.create_policy("get-s3-object", "get-from-bucket-policy.json")
    chc.attach_role_policy("web-serv-role", "arn:aws:iam::025507102606:policy/get-s3-object")
    time.sleep(1)


    chc.create_instance_profile("web-serv-prof")
    chc.add_role_to_instance_profile("web-serv-prof", "web-serv-role")
    time.sleep(1)

    chc.create_instance_key_pair("web-serv-keypair")

    chc.create_security_group("web-serv-sg", "for the web server")
    chc.allow_port_security_group("web-serv-sg", 22)
    chc.allow_port_security_group("web-serv-sg", 80)
    time.sleep(1)
    
    chc.create_instance("web-serv-keypair", "web-serv-prof", "WebServ", "web-serv-sg",\
            "web-server.sh")

