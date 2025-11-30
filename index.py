import csv
import json
from flask import Flask, render_template
import d3_network as d3
import os

cf_port = os.getenv("PORT")

#position1 = "User111"
# reference: https://stackoverflow.com/questions/29631711/python-to-parent-child-json

# create a helper class for each tree node
class Node(object):
    # generate new node
    def __init__(self, cluster):
        self.cluster = cluster
        self.children = []

    # append a child node to parent (self)
    def child(self, child_cluster):
        # check if child already exists in parent
        child_found = [c for c in self.children if c.cluster == child_cluster]
        if not child_found:
            # if it is a new child, create new node for this child
            _child = Node(child_cluster)
            # append new child node to parent's children list
            self.children.append(_child)
        else:
            # if the same, save this child
            _child = child_found[0]
        # return child object for later add
        return _child

    # convert the whole object to dict
    def as_dict(self):
        res = {'cluster': self.cluster}
        res['children'] = [c.as_dict() for c in self.children]
        return res

# drive function
app = Flask(__name__)

@app.route('/graph/<position1>', methods=['GET'])
def create_tree(position1):
    #position1 = "User222"
    d3.webhook(position1)
    root = Node('Quick Info')
    cluster_levels = 5

    #f = d3.webhook(position1)
    with open('out.csv', 'r') as f:
        #print(f)
        reader = csv.reader(f)
        #print(reader)
        # skip header row
        next(reader)
        # scan data by row
        for row in reader:
            parent = root
            # cluster info: from column 1 to 3
            for level in range(1, (cluster_levels + 1)):
                parent = parent.child(row[level])
                #print(parent)
    # print(json.dumps(root.as_dict(), indent=4))
    return render_template('index.html', data = json.dumps(root.as_dict()))



port = int(os.getenv("PORT", 0))
if __name__ == '__main__':
    if port != 0:
        app.run(host='0.0.0.0', port=cf_port)
    else:
        app.run()
