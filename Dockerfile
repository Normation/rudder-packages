FROM rust:1.82

#FROM debian:12
#
#RUN apt-get update && apt-get install -y shellcheck
RUN cargo install --locked -f typos-cli
RUN apk update && apk add shellcheck
