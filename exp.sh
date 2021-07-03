#!/bin/sh
cd bust
cargo build --release
cp ./target/release/bust.dll ../lib/bust.pyd
