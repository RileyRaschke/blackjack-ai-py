#!/usr/bin/env python3

import os
import sys
import argparse
import json

opts = argparse.ArgumentParser(
    description=""
)
opts.add_argument('-i','--interactive', action='store_true',
    help='interactive, Enable the human player.')

opts.add_argument('-d','--decks', type=int,
    help='Number of decks in each shoe')

opts.add_argument('-s','--shoes', type=int,
    help='Number of shoes (games) to play')

args = opts.parse_args()

import importlib
import pkgutil

import player.players

from game.game   import Game

def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

game_opts = {
    'shoes': args.shoes or 1,
    'decks': args.decks or 6,
    'hitSoft17': True,
    'insurance': True,
}

table_seats = {
    name: importlib.import_module(name)
        for finder, name, ispkg in iter_namespace(player.players)
            if name != 'player.players.human' or args.interactive
}

game = Game( game_opts, table_seats )

game.play()

