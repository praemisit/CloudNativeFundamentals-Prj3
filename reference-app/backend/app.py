import opentracing.tracer
from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
import logging
from jaeger_client import Config
from flask_opentracing import FlaskTracing




app = Flask(__name__)


# Added code for Jaeger Tracer
config = Config(
    config={
        'sampler':
        {'type': 'const',
         'param': 1},
                        'logging': True,
                        'reporter_batch_size': 1,}, 
                        service_name="backend-service")
jaeger_tracer = config.initialize_tracer()
tracing = FlaskTracing(jaeger_tracer, True, app)


app.config['MONGO_DBNAME'] = 'example-mongodb'
app.config['MONGO_URI'] = 'mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb'

mongo = PyMongo(app)
parent_span = tracing.get_span()


@app.route('/')
def homepage():
    with opentracing.tracer.start_span("homepage", child_of=parent_span) as span:
        response = {"message": "homepage"}
        span.set_tag('message', response)
        return "Hello World"


@app.route('/api')
def my_api():
    with opentracing.tracer.start_span("api", child_of=parent_span) as span:
        response = {"message": "api"}
        span.set_tag("message", response)

        answer = "something"
        return jsonify(response=answer)


@app.route('/star', methods=['POST'])
def add_star():
    with opentracing.tracer.start_span("star", child_of=parent_span) as span:
        try:
            star = mongo.db.stars
            name = request.json['name']
            distance = request.json['distance']
            star_id = star.insert({'name': name, 'distance': distance})
            new_star = star.find_one({'_id': star_id})
            output = {'name': new_star['name'], 'distance': new_star['distance']}
            return jsonify({'result': output})
        except:
            span.set_tag("response", "Error: cannot access the database.")


if __name__ == "__main__":
    app.run()