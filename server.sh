#!/usr/bin/env bash

tmux new -s rachni -d
tmux split-window -v -t rachni

tmux send-keys -t rachni:1.0 'workon rachni' C-m
tmux send-keys -t rachni:1.0 './run.py' C-m
tmux send-keys -t rachni:1.1 'workon rachni' C-m
tmux send-keys -t rachni:1.1 './mserver/run.py' C-m

tmux attach -t rachni
