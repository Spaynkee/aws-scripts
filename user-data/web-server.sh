#!/bin/bash 

yum -y update;
yum install -y python3-pip;
yum install -y git;
yum install -y cmake;
yum install -y gcc;
yum install -y openssl-devel;
amazon-linux-extras install -y nginx1;
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -y;

export PATH=$PATH:~/.cargo/bin

curl -sL https://rpm.nodesource.com/setup_10.x | bash -;
yum install -y nodejs;

git clone https://github.com/Spaynkee/lol-data.git ;
mv lol-data/ /usr/share/nginx/;

aws s3 cp s3://super-cool-bucket-1337-pb/nginx.conf /etc/nginx/nginx.conf ;
aws s3 cp s3://super-cool-bucket-1337-pb/lol-data_nginx.conf /etc/nginx/conf.d/lol-data_nginx.conf ;

/usr/sbin/nginx ;

cd /usr/share/nginx/lol-data;
npm install;
npm run build;
pip3 install -r requirements.txt

aws s3 cp s3://super-cool-bucket-1337-pb/config.toml /usr/share/nginx/lol-data/config.toml;
aws s3 cp s3://super-cool-bucket-1337-pb/general.cfg /usr/share/nginx/lol-data/resources/python/general.cfg;

cp resources/python/scripts/data_base_setup_v2.py resources/python/data_base_setup_v2.py;

cp resources/python/scripts/league_user_table_setup.py resources/python/league_user_table_setup.py;

python3 resources/python/data_base_setup_v2.py;
python3 resources/python/league_user_table_setup.py;

rm resources/python/data-base-setup-v2.py;
rm resources/python/league_user_table_setup.py;

# run the data population sript
python3 resources/python/update_db_from_api.py;


cargo run;

