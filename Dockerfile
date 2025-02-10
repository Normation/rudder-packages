# rust is a debian based image with rust preinstalled
FROM rust

RUN apt-get update && apt-get install -y shellcheck
RUN cargo install -f typos-cli
