# Choropy

Choropy is a little python script that helps you to generate GeoJSON for choropleth maps with jenks natural breaks. Optionally it saves a HTML-file with a functional choropleth-map written in d3.js. You can choose between a blue, a red and a green color scheme.

All you need to do is providing a data csv-file and a GeoJSON-file. The script does nearly all the work for you. Afterwards you probably need to change scaling, some headlines, the clicked-function and some styling.

![example](https://raw.githubusercontent.com/dahilzen/choropy/master/example.png)

## Requirements

You need to install the following modules:
+ argparse
+ pandas
+ geopandas
+ numpy
+ jenkspy

I recommend using Anaconda/Miniconda.
```
conda install -c conda-forge argparse pandas geopandas numpy jenkspy
```

Or just install the requirements.txt with
```
conda install --file requirements.txt
```

## Usage

The script needs a data file with the flag -i and a geojson file with the flag -j

```
python choro.py -i data.csv -j shape.json
```

Of course the files need to have a shared key so they can be merged. You need to specify this variable through out the process.

## To Do

+ optionally use TopoJSON instead of GeoJSON
+ support for other file types like shapefile, tsv, etc.

