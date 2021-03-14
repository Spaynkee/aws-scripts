#!/bin/bash 

# I'm being told sudo is not needed for user data scripts because it runs as root anyway. Fix me later
sudo yum -y update;
sudo yum install -y python3-pip;
sudo yum install -y git;
sudo yum install -y cmake;
sudo yum install -y gcc;
sudo yum install -y openssl-devel;
sudo amazon-linux-extras install -y nginx1;
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -y;
source $HOME/.cargo/env;

curl -sL https://rpm.nodesource.com/setup_10.x | sudo bash -;
sudo yum install -y nodejs;

git clone https://github.com/Spaynkee/lol-data.git ;
sudo mv lol-data/ /usr/share/nginx/;

aws s3 cp s3://super-cool-bucket-1337-pb/nginx.conf /etc/nginx/nginx.conf ;


aws s3 cp s3://super-cool-bucket-1337-pb/lol-data_nginx.conf /etc/nginx/conf.d/lol-data_nginx.conf ;

sudo /usr/sbin/nginx ;

cd /usr/share/nginx/lol-data;
npm install;
npm run build;

# f it, we don't need a db yet. If we can get the front end working then I'll take it.

# cargo run isn't working on the instance, it seems.
cargo run

