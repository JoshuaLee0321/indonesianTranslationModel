from flask import Flask, request, jsonify, render_template
from flask_restful import Resource, Api, abort, reqparse
from scripts import translate, services
import hanlp
# flask
app = Flask(__name__)
api = Api(app)
# hanlp pipeline
# import hanlp
pipe = hanlp.pipeline().append(hanlp.utils.rules.split_sentence, output_key='sentences')\
                        .append(hanlp.load('FINE_ELECTRA_SMALL_ZH'), output_key='tok')\
                        .append(hanlp.load('CTB9_POS_ELECTRA_SMALL'), output_key='pos')

@app.errorhandler(400)
def bad_request_handler(message):
    '''
    User bad request handler
    '''
    return jsonify(error=str(message)), 400

class Translation(Resource):
    def get(this):
        try:
            return jsonify({"translate": {'Translation_model': 'idn'}})
        except Exception as e:
            abort(400, 'translation failed')

    def post(this):
        '''
        input : translate word
        output: jsonfile of translated word
        '''
        # parse args
        parser = reqparse.RequestParser()
        parser.add_argument('translation_text', required=True)
        parser.add_argument('model', required=True)
        args = parser.parse_args()

        # generate translation
        text = services.translation(args, pipe)
    
        # return None if model not found
        if  text == None:
            return jsonify({"message" : f"current model does not support {args['model']}"})            

        app.logger.info('[ %s ] translated into [ %s ]', args['translation_text'], text)
        return jsonify({"message": "success", "before_translation": args['translation_text'], "after_translation": text})

api.add_resource(Translation, '/translation')


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=1002, debug=True)
