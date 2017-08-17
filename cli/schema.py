
import sys
import json

from tabulate import tabulate

from fastscore import Schema
from fastscore import FastScoreError

def add(connect, name, schema_file=None, verbose=False, **kwargs):
    try:
        if schema_file:
            with open(schema_file) as f:
                source = f.read()
        else:
            source = sys.stdin.read()
        schema = Schema(name, json.loads(source))
    except Exception as e:
        raise FastScoreError("Unable to add schema '%s'" % name, caused_by=e)
    mm = connect.lookup('model-manage')
    updated = schema.update(mm)
    if verbose:
        print "Schema updated" if updated else "Schema created"

def show(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    schema = mm.schemata[name]
    print json.dumps(schema.source, indent=2)

def remove(connect, name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    del mm.schemata[name]
    if verbose:
        print "Schema removed"

def roster(connect, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    if verbose:
        t = [ [x,'Avro'] for x in mm.schemata.names() ]
        print tabulate(t, headers=["Name","Type"])
    else:
        for x in mm.schemata.names():
            print x
