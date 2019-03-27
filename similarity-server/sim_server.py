from flask import Flask, request
import tf_similarity as TFS

# Init app 
app = Flask(__name__)

# Load model
tfs = TFS.TfSimilarity()

@app.route('/', methods=['GET'])
def test():
    return 'test'

@app.route('/gs', methods=['GET'])
def get_similarity():
    arg0 = request.form.get('phrase1')
    arg1 = request.form.get('phrase2')
    return '{}'.format(tfs.get_similarity(arg0, arg1))
