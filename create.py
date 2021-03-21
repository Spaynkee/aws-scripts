""" create.py

    This script creates a number of aws resources and configures everything needed to run a website
    with a database on said resources.
"""

import time
from ch_create import CHCreate

if __name__ == "__main__":
    chc = CHCreate()

    # start rds
    chc.create_security_group("rds-sg", "for the db")
    chc.allow_port_security_group("rds-sg", 3306)
    chc.allow_port_security_group("rds-sg", 22)
    time.sleep(1)

    chc.create_rds_instance("rds-is-cool", "rds-sg")

    # while the DB is coming up we can do everything else for the webserver
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

    # these depend on the rds and are required by the web serv.
    chc.create_config("general.cfg")
    chc.create_config("config.toml")

    chc.create_instance("web-serv-keypair", "web-serv-prof", "WebServ", "web-serv-sg",\
            "web-server.sh")
