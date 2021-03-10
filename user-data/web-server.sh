#!/bin/bash 
sudo yum update
sudo yum installi -y python3-pip
sudo yum install -y git
sudo yum install -y cmake
sudo yum install -y gcc
sudo yum install -y openssl-devel
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -u
source $HOME/.cargo/env

git clone https://github.com/Spaynkee/lol-data.git
cd /lol-data
# we need some data first.. and we need an nginx setup? This is where it gets a bit more complicated.

cargo run

