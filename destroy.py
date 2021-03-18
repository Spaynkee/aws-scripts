from CHDelete import CHDelete

if __name__ == "__main__":
    chd = CHDelete()
    chd.remove_role_from_instance_profile("web-serv-prof", "web-serv-role")
    chd.detach_role_policy("web-serv-role", "arn:aws:iam::025507102606:policy/get-s3-object")
    chd.destroy_policy("arn:aws:iam::025507102606:policy/get-s3-object")
    chd.destroy_role("web-serv-role")

    chd.destroy_instance_key_pair("web-serv-keypair")
    chd.destroy_instance_profile("web-serv-prof")
    chd.destroy_instance("WebServ")
    chd.destroy_security_group("web-serv-sg")

    chd.destroy_rds_instance("rds-is-cool")
    chd.destroy_security_group("rds-sg")
