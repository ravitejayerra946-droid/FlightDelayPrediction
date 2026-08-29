from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

# Load trained machine learning models
classifier = joblib.load("random_forest_classifier.pkl")
regressor = joblib.load("random_forest_regressor.pkl")

# Load encoders and feature order
encoders = joblib.load("label_encoders.pkl")
feature_columns = joblib.load("feature_columns.pkl")

airline_encoder = encoders["airline_encoder"]
airport_encoder = encoders["airport_encoder"]


@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    form_data = {}

    if request.method == "POST":

        # Save all values entered by the user
        form_data = request.form.to_dict()

        try:

            # Get values entered by the user
            year = float(request.form["Year"])
            month = float(request.form["Month"])

            airline = int(request.form["AirlineCode"])
            airport = int(request.form["AirportCode"])

            total_flights = float(request.form["TotalFlights"])
            flights_delayed = float(
                request.form["FlightsDelayedOver15Min"]
            )

            carrier_delay = float(
                request.form["CarrierDelayCount"]
            )

            weather_delay = float(
                request.form["WeatherDelayCount"]
            )

            nas_delay = float(
                request.form["NASDelayCount"]
            )

            security_delay = float(
                request.form["SecurityDelayCount"]
            )

            late_aircraft_delay = float(
                request.form["LateAircraftDelayCount"]
            )

            cancelled = float(
                request.form["CancelledFlights"]
            )

            diverted = float(
                request.form["DivertedFlights"]
            )


            # Encode Airline and Airport
            airline_encoded = airline_encoder.transform(
                [airline]
            )[0]

            airport_encoded = airport_encoder.transform(
                [airport]
            )[0]


            # Create input data
            input_data = {

                "Year": year,
                "Month": month,
                "AirlineCode": airline_encoded,
                "AirportCode": airport_encoded,
                "TotalFlights": total_flights,
                "FlightsDelayedOver15Min": flights_delayed,
                "CarrierDelayCount": carrier_delay,
                "WeatherDelayCount": weather_delay,
                "NASDelayCount": nas_delay,
                "SecurityDelayCount": security_delay,
                "LateAircraftDelayCount": late_aircraft_delay,
                "CancelledFlights": cancelled,
                "DivertedFlights": diverted
            }


            # Create DataFrame
            input_df = pd.DataFrame([input_data])

            # Make sure feature order matches training
            input_df = input_df[feature_columns]


            # Classification prediction
            classification_prediction = classifier.predict(
                input_df
            )[0]


            # Regression prediction
            regression_prediction = regressor.predict(
                input_df
            )[0]


            # Convert classification result
            if classification_prediction == 1:
                classification = "Delayed"
            else:
                classification = "Not Delayed"


            # Store results
            result = {

                "classification": classification,

                "delay_minutes": round(
                    float(regression_prediction),
                    2
                )
            }


        except Exception as e:

            result = {
                "error": str(e)
            }


    return render_template(
        "index.html",
        result=result,
        form_data=form_data
    )


if __name__ == "__main__":

    app.run(
        debug=False,
        port=5001
    )