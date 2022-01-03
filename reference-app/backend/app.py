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


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


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



@app.route("/403")
def status_code_403():
    status_code = 403
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )

@app.route("/404")
def status_code_404():
    status_code = 404
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )

@app.route("/500")
def status_code_500():
    status_code = 500
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )

@app.route("/503")
def status_code_503():
    status_code = 503
    raise InvalidUsage(
        "Raising status code: {}".format(status_code), status_code=status_code
    )



if __name__ == "__main__":
    app.run()