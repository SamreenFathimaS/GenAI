from flask import Flask

app=Flask(__name__)


@app.route('/')
def hello():
    return("Welcome tothe our family to join and enjoy with much happiness and god blesses")



if __name__=='__main__':
 app.run(debug=True)