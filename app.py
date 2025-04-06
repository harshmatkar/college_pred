from flask import Flask, render_template, request, send_file
import pandas as pd
import numpy as np
from io import BytesIO

app = Flask(__name__)

# TEMPORARY variable to store result across requests
latest_result = []

@app.route('/' , methods = ['GET', 'POST'])
def home():
    global latest_result  # to store the result globally
    result_table = None
    result_heading = ""
    if request.method == "POST":
        print("Form Data:", request.form) 
        upper = int(request.form.get('upperLimit'))
        lower = int(request.form.get('lowerLimit'))
        category = request.form.get('category')
        gender = request.form.get('gender')
        exam = request.form.get('exam')
        
        result_heading = f"Results for {category} - {gender} between ranks {lower} and {upper}"
        
        # Load and filter data
        if exam == "JEE MAIN" :
            data = pd.read_csv("jossa R5 cutoffCSV.csv")
            new_data = data[data["Seat Type"] == category]
            filterd_data = new_data[(new_data["Closing Rank"] > lower) & (new_data["Closing Rank"] < upper)]
            if gender == "Female":
                gender = "Female-only (including Supernumerary)"
            hs_data = filterd_data[(filterd_data["Quota"] == "HS") & (filterd_data["Gender"] == gender)]
            os_data = filterd_data[(filterd_data["Quota"] == "OS") & (filterd_data["Gender"] == gender)]
            
            hs_data.sort_values("Closing Rank", inplace=True)
            os_data.sort_values("Closing Rank", inplace=True)
            
            combined_data = pd.concat([os_data, hs_data], ignore_index=True)
            result_table = combined_data.to_dict(orient='records')
            
            latest_result = result_table  # Store latest result for download
        
        elif exam == "JEE ADVANCED" :
            data = pd.read_csv("vscodeiitcuoff.csv")
            new_data = data[data["Category"] == category]
            new_data["Closing Rank"] = pd.to_numeric(new_data["Closing Rank"], errors='coerce')
            filterd_data = new_data[(new_data["Closing Rank"] > lower) & (new_data["Closing Rank"] < upper)]
            if gender == "Female":
                gender = "Female-only (including Supernumerary)"
            AI_data = filterd_data[(filterd_data["Seat type"] == "AI") & (filterd_data["Gender"] == gender)]
            
            AI_data.sort_values("Closing Rank", inplace=True)
            
            result_table = AI_data.to_dict(orient='records')
            
            latest_result = result_table  # Store latest result for download

    return render_template('home.html', result = result_table, result_heading=result_heading)

@app.route('/download')
def download():
    global latest_result
    if not latest_result:
        return "No data to download. Please submit the form first."

    df = pd.DataFrame(latest_result)
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(output,
                     download_name='jossa_filtered_data.csv',
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)
