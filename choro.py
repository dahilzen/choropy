#!/usr/bin/python

#read in modules
from argparse import ArgumentParser
import os.path
import json
import pandas as pd
import geopandas as gpd
import numpy as np
from datetime import datetime
import jenkspy

# check if files do exist
def is_valid_file(parser, arg):
  ext = os.path.splitext(arg)[1][1:]
  if not os.path.exists(arg):
    parser.error("The file %s does not exist!" % arg)
  elif ext not in ['csv','geojson','json']:
    parser.error('The file %s does not have the right extension. The script only reads csv, json or geojson.' % arg)
  else:
    return open(arg, 'r')  # return an open file handle


# read in arguments/files
parser = ArgumentParser()
parser.add_argument("-i", dest="csv", required=True,
                    help="input file", metavar="string",
                    type=lambda x: is_valid_file(parser, x))
parser.add_argument("-j", dest="shape", required=True,
                    help="input file", metavar="string",
                    type=lambda x: is_valid_file(parser, x))

args = parser.parse_args()

# save files as dataframes...
df = pd.read_csv(args.csv, dtype=object)
gdf = gpd.read_file(args.shape.name)

gdf = gdf.to_crs(epsg=4326)

print('Choose variables to merge on')
print('-----')
print('These are the variables of the shape file:')
print(np.array(gdf.columns))
left = input('which one to choose? ')
print('-----')
print('These are the variables of the data file:')
print(np.array(df.columns))
right = input('which one to choose? ')
print('-----')

#...merge dataframes
gdf = gdf.merge(df,left_on=left, right_on=right)


print(np.array(gdf.columns))
data = input('which variable do you want to show? ')
print('-----')
gdf[data] = pd.to_numeric(gdf[data])

# generate natural breaks
breaks = jenkspy.jenks_breaks(gdf[data], nb_class=5)

print('These are the breaks:')
print(breaks)
print('-----')

# prompt to generate colors
blue = ['#eff3ff','#bdd7e7','#6baed6','#3182bd','#08519c']
green = ['#edf8e9','#bae4b3','#74c476','#31a354','#006d2c']
red = ['#fee5d9','#fcae91','#fb6a4a','#de2d26','#a50f15']

col = input('do you want blue, red or green color scheme? ')

def return_color(col):
    if (col == 'blue'):
        return blue
    elif (col == 'red'):
        return red
    else: return green

color = return_color(col)

farbe = {
    breaks[1]: color[0],
    breaks[2]: color[1],
    breaks[3]: color[2],
    breaks[4]: color[3],
    breaks[5]: color[4]
}

def get_color(wert):
    for i in farbe:
        if (wert >= breaks[-1]):
            return farbe[breaks[-1]]
        elif (wert <= i):
            return farbe[i]
            break

gdf['color'] = gdf[data].apply(get_color)

#save dataframe as geojson
now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = 'output_'+now+'.json'
gdf.to_file(filename, driver="GeoJSON")

print('you can find your geojson here: ' + filename)
print('-----')

def save_txt():
    test ="""
    <!DOCTYPE html>
<meta charset='utf-8'>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />

<style>
html {
    font-family: Open Sans, Sans-Serif;
    color: #3a3b42;
    font-size: 14px;
    word-wrap: break-word;
    height: 100%
}

path {
    stroke-width: 1px;
    stroke: white;
    cursor: pointer;
}

path:hover,
path.highlighted {
    fill: black;
    stroke-width: 2px;
}

h2,
h3 {
    text-align: center;
}

#map {
    width: 100% !important;
    height: 600px !important;
}

@media screen and (max-width: 420px) {
    #map {
        width: 100% !important;
        height: 430px !important;
    }
}

</style>

<body>
    <div id='map'>
        <h2 id='headline'>Dies ist eine Überschrift</h2>
        <h3 id='subline'>Klicken Sie auf einen Kreis</h3>
        <svg></svg>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@turf/turf@5/turf.min.js"></script>
    <script src='http://d3js.org/d3.v4.min.js'></script>
    <script>
    var color = """ + str(color) + """;
    var breaks = """ + str(breaks) + """;

    var map = d3.select('#map');

    //Map dimensions
    var width = parseFloat(map.style('width'));
    var height = parseFloat(map.style('height'));

    //Map projection
    var projection = d3.geoMercator()
        .scale(9551.989231882751)
        .translate([width / 2, height / 2]); //translate to center the map in view

    //Generate paths based on projection
    var path = d3.geoPath()
        .projection(projection);

    //Create an SVG
    var svg = d3.select('svg')
        .attr('width', width)
        .attr('height', height + 100);

    //Group for the map features
    var features = svg.append('g')
        .attr('class', 'features');

    d3.json('""" + filename + """', function(error, geodata) {
        if (error) return console.log(error); //unknown error, check the console

        var center = turf.center(geodata).geometry.coordinates;
        projection.center(center); //projection center

        //Create a path for each map feature in the data
        features.selectAll('path')
            .data(geodata.features)
            .enter()
            .append('path')
            .attr('d', path)
            .style('fill', function(d) {
                return d.properties.color;
            })
            .on('click', clicked)
            .on('mouseover', function(d) {
                d3.select(this).style('fill', 'lightyellow');
            })
            .on('mouseout', function(d) {
                d3.select(this).style('fill', function(d) {
                    return d.properties.color;
                });
            });

        var legend = svg.append('g')
            .attr('class', 'legend')
            .selectAll('g')
            .data(color)
            .enter()
            .append('g')
            .attr('class', 'legenditem')
            .attr('transform', function(d, i) {
                var x = i * 50 + (width / 2 - 125);
                var y = height;
                return 'translate(' + x + ',' + y + ')';
            });

        legend.append('rect')
            .attr('class', 'rect')
            .attr('width', 50)
            .attr('height', 10)
            .style('fill', function(d) {
                return d;
            });

        var legendNodes = svg.selectAll('.legenditem')._groups[0];

        d3.select(legendNodes[0])
            .append('text')
            .text(breaks[0])
            .attr('transform', function() {
                var x = -7;
                var y = 25;
                return 'translate(' + x + ',' + y + ')';
            });

        d3.select(legendNodes[4])
            .append('text')
            .text(breaks[5])
            .attr('transform', function() {
                var x = 30;
                var y = 25;
                return 'translate(' + x + ',' + y + ')';
            });

        d3.select(legendNodes[2])
            .append('text')
            .text('Count')
            .attr('transform', function() {
                var x = 5;
                var y = -10;
                return 'translate(' + x + ',' + y + ')';
            });

    });

    // Add optional onClick events for features here
    // d.properties contains the attributes (e.g. d.properties.name, d.properties.population)
    function clicked(d) {
        var subline = d3.select('#subline');
        subline.html(d.properties.Name + ': ' + d.properties.count);
    }
    </script>"""

    with open(output_name+'.html', 'w') as text_file:
        text_file.write(test)

js = input('do you want to generate a map? (yes/no) ')
print('-----')

if (js == 'yes'):
    output_name = input('name your html-file: ')
    print('***********')
    print('ATTENTION: You probably need to change scaling, some headlines, the clicked-function and some styling.')
    print('***********')
    save_txt()
else: pass
