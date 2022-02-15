from flask import Flask,render_template,request,session,redirect,url_for
#from module import prediction
import numpy as np
import pickle

app = Flask(__name__)
app.secret_key="checkout"
modelm=pickle.load(open('model1.pkl','rb'))

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/model', methods=["POST", "GET"])
def model():
    if request.method=='POST':
        trustLevel=request.form['trustLevel']
        totalScanTimeInSeconds=request.form['totalScanTimeInSeconds']
        lineItemVoids=request.form['lineItemVoids']
        scansWithoutRegistration=request.form['scansWithoutRegistration']
        quantityModifications=request.form['quantityModifications']
        scannedLineItemsPerSecond=request.form['scannedLineItemsPerSecond']
        valuePerSecond=request.form['valuePerSecond']
        lineItemVoidsPerPosition=request.form['lineItemVoidsPerPosition']
        

        session['trustLevel']=trustLevel
        session['totalScanTimeInSeconds']=totalScanTimeInSeconds
        session['lineItemVoids']=lineItemVoids
        session['scansWithoutRegistration']=scansWithoutRegistration
        session['quantityModifications']=quantityModifications
        session['scannedLineItemsPerSecond']=scannedLineItemsPerSecond
        session['valuePerSecond']=valuePerSecond
        session['lineItemVoidsPerPosition']=lineItemVoidsPerPosition
        return redirect(url_for('predict_m'))
    else:  
        return render_template('model.html')

@app.route('/prediction')
def predict_m():
    session['totalScanned'] = session['scannedLineItemsPerSecond'] * session['totalScanTimeInSeconds']
    # avgValuePerScan:
    session['avgTimePerScan'] = 1/ session['scannedLineItemsPerSecond']
    session['avgValuePerScan'] = session['avgTimePerScan'] * session['valuePerSecond']
    # manual feature generation - "totalScanned" ratios
    # withoutRegisPerPosition
    session['withoutRegisPerPosition'] = session['scansWithoutRegistration'] / session['totalScanned']
    # ratio of scansWithoutRegis in totalScan
    # equivalent to lineItemVoidsPerPosition
    # Might indicate how new or ambivalent a customer is. Expected to be higher for low "trustLevel"
    # quantiModPerPosition
    session['quantiModPerPosition'] = session['quantityModifications'] / session['totalScanned']
    # ratio of quanityMods in totalScan
    # manual feature generation - "grandTotal" ratios
    # lineItemVoidsPerTotal
    session['lineItemVoidsPerTotal'] = session['lineItemVoids'] / session['grandTotal']
    # withoutRegisPerTotal
    session['withoutRegisPerTotal'] = session['scansWithoutRegistration'] / session['grandTotal']
    # quantiModPerTotal
    session['quantiModPerTotal'] = session['quantityModifications'] / session['grandTotal']
    # manual feature generation - "totalScanTimeInSeconds" ratios
    # lineItemVoidsPerTime
    session['lineItemVoidsPerTime'] = session['lineItemVoids'] / session['totalScanTimeInSeconds']
    # withoutRegisPerTime
    session['withoutRegisPerTime'] = session['scansWithoutRegistration'] / session['totalScanTimeInSeconds']
    # quantiModPerTime
    session['quantiModPerTime'] = session['quantityModifications'] / session['totalScanTimeInSeconds']

    input_data=[session['trustLevel'], session['totalScanTimeInSeconds'], session['grandTotal'], session['lineItemVoids'],
       session['scansWithoutRegistration'], session['quantityModifications'],
       session['scannedLineItemsPerSecond'], session['valuePerSecond'],
       session['lineItemVoidsPerPosition'], session['totalScanned'], session['avgTimePerScan'],
       session['avgValuePerScan'], session['withoutRegisPerPosition'], session['quantiModPerPosition'],
       session['lineItemVoidsPerTotal'], session['withoutRegisPerTotal'], session['quantiModPerTotal'],
       session['lineItemVoidsPerTime'], session['withoutRegisPerTime'], session['quantiModPerTime']]
    input_data = np.asarray(input_data)
    input_data_reshaped = input_data.reshape(1,-1)
    prediction=modelm.predict(input_data_reshaped)

    if prediction[0]==0:
        reverb ='not fraud'
    else:
        reverb ='fraud'
    return render_template('prediction.html',predicts=reverb)

if __name__ == "__main__":
    app.run(debug=True)