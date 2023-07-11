import argparse
import json
import logging
import os
import sys

from jinja2 import Environment, FileSystemLoader, Template

sys.path.insert(0, '/Users/corywatson/src/signalfx-python')

import signalfx

COLORS = [
    "gray",
	"blue",
	"blue",
	"navy",
	"orange",
	"orange",
	'yellow',
	'magenta',
	'cerise',
	'pink',
	'violet',
	'purple',
	'gray_blue',
	'dark_green',
	'green',
	'aquamarine',
	'red',
	'yellow',
	'yellow',
	'green',
	'green'
]

def do_chart(client, chartId, name):
    c = client.get_chart(chartId)
    c['terraformName'] = name
    if c['options']['type'] == 'TimeSeriesChart':
        do_time_chart(client, c, name)
    elif c['options']['type'] == 'List':
        do_list_chart(client, c, name)
    elif c['options']['type'] == 'SingleValue':
        do_single_value_chart(client, c, name)
    else:
        print("Chart type not implemented")
        print(chartId)

def resolve_color(index):
    return COLORS[index]

def do_list_chart(client, chart, name):
    print(list_chart_template.render(chart))

def do_single_value_chart(client, chart, name):
    print(single_value_chart_template.render(chart))

def do_dashboard(client, dashboardId, name):
    d = client.get_dashboard(dashboardId)
    d['terraformName'] = name
    print(dashboard_template.render(d))

def do_detector(client, detectorId, name):
    d = client.get_detector(detectorId)
    d['terraformName'] = name
    print(detector_template.render(d))

def do_time_chart(client, chart, name):
    print(time_chart_template.render(chart))

parser = argparse.ArgumentParser()

parser.add_argument('--realm', help='SignalFx Realm (defaults to none)')
parser.add_argument('--verbose', help='Be verbose', action='store_const', const=True )
parser.add_argument('--chart', help='A chart to convert')
parser.add_argument('--dashboard', help='A dashboard to convert')
parser.add_argument('--detector', help='A detector to convert')
parser.add_argument('--name', help='Terraform name of resulting asset', required=True)

args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

if 'SFX_AUTH_TOKEN' not in os.environ:
    logging.error('ERROR: Please specify an SFx auth token via SFX_AUTH_TOKEN')
    sys.exit(1)
sfx_api_key = os.environ['SFX_AUTH_TOKEN']

templateLoader = FileSystemLoader(searchpath="./")
env = Environment(loader=templateLoader, trim_blocks=True, lstrip_blocks=True)

single_value_chart_template = env.get_template('single_value_chart_template.tf.j2')
dashboard_template = env.get_template('dashboard_template.tf.j2')
detector_template = env.get_template('detector_template.tf.j2')
list_chart_template = env.get_template('list_chart_template.tf.j2')
time_chart_template = env.get_template('time_chart_template.tf.j2')

if args.chart is None and args.dashboard is None and args.detector is None:
    sys.exit('Please supply a chart, dashboard, or detector ID to export')

if __name__ == "__main__":
    sfx = signalfx.SignalFx()
    if args.realm is not None:
        # Use a realm if we get one
        sfx = signalfx.SignalFx(api_endpoint='https://api.' + args.realm + '.signalfx.com')

    with sfx.rest(sfx_api_key) as rest:
        def do_chart_template(chartId):
            do_chart(rest, chartId, 'TKTKnamehere')

        env.globals.update(do_chart=do_chart_template)
        env.globals.update(resolve_color=resolve_color)

        if args.chart:
            do_chart(rest, args.chart, args.name)
        elif args.dashboard:
            do_dashboard(rest, args.dashboard, args.name)
        elif args.detector:
            do_detector(rest, args.detector, args.name)
