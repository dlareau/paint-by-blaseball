# paint-by-blaseball

## What is this?
Paint-by-Blaseball is an entry into the [SIBR cursed viewer contest](https://cursed.sibr.dev). It is a way of fitting a whole season of blaseball (every single update from every single game) into a single image viewable all at once on a large enough monitor. 

## Please show me an example.
Okay here, this is all of season 22:
![An example rendered season](/season22.png)

## What am I looking at?
The image is made up of "cells" each representing a single game update. Every game from the season is represented as a column of cells with the game progressing from the top of the column to the bottom of the column in order. Each cell has enough information to reasonably re-construct the general state as it would have been shown on www.blaseball.com (the only loss of data is just having the feed type of an update instead of the exact game update text).

Here is a close up of a cell and what each part of it means:
![An image explaining a single update tile](/explainer.png)

## Why does the image look red?
To better distinguish individual cells when zoomed in, each cell has a red border around it.

## Why red as a border color?
🩸🩸🩸
