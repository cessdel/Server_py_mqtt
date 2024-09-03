from influxdb_client import InfluxDBClient
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from localStoragePy import localStoragePy
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import logging
localStorage = localStoragePy('my_app_namespace', 'json')


DB_PORT = localStorage.getItem('influx_port')
DB_HOST = localStorage.getItem('influx_host')
DB_ORG = localStorage.getItem('influx_org')
DB_TOKEN = localStorage.getItem('influx_token')
DB_BUCKET = localStorage.getItem('influx_bucket')
url=f'http://{str(DB_HOST)}:{str(DB_PORT)}'

class TemperatureModel:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = self.load_model()
        self.client = InfluxDBClient(
            url=url,
            token=DB_TOKEN,
            org=DB_ORG,
        )
        self.training_status = "Not started"

    def load_model(self):
        try:
            model = joblib.load(self.model_path)
            logging.info("Model loaded successfully.")
            print("Model loaded successfully.")
        except FileNotFoundError:
            model = LinearRegression()  # Modelo por defecto si no existe
            logging.error("Model not found, initialized a new LinearRegression model.")
            print("Model not found, initialized a new LinearRegression model.")
        return model

    def save_model(self):
        joblib.dump(self.model, self.model_path)
        logging.info("Model saved to %s", self.model_path)
        print(f"Model saved to {self.model_path}")

    def train_model(self):
        logging.info("Training started.")
        print("Training started.")
        self.training_status = "In progress"
        try:
            query_api = self.client.query_api()
            query = f"""
            from(bucket: "{DB_BUCKET}")
                |> range(start: -50d)  // Ajusta el rango para el entrenamiento
                |> filter(fn: (r) => r["_measurement"] == "temperatura")
                |> keep(columns: ["_time", "_value"])
            """
            tables = query_api.query(query)

            data = []
            times = []

            for table in tables:
                for record in table.records:
                    times.append(record.get_time())
                    data.append(record.get_value())

            df = pd.DataFrame({'time': times, 'temperature': data})
            df['timestamp'] = df['time'].astype(np.int64) // 10**9  # Convertir a segundos desde epoch

            X = df['timestamp'].values.reshape(-1, 1)
            y = df['temperature'].values

            self.model.fit(X, y)
            self.save_model()

            y_pred_train = self.model.predict(X)
            mse = mean_squared_error(y, y_pred_train)
            mae = mean_absolute_error(y, y_pred_train)
            r2 = r2_score(y, y_pred_train)

            logging.info(f"Training completed.\nMean Squared Error (MSE): {mse}\nMean Absolute Error (MAE): {mae}\nR²: {r2}")
            self.training_status = "Completed"

        except Exception as e:
            logging.error("Error during training: %s", e)
            print(f"Error during training: {e}")
            self.training_status = "Failed"

    def predict_future_temperatures(self, hours=12):
        now = datetime.now()  # Utiliza UTC
        print(f"Current time: {now}")
        next_hour = (now + timedelta(hours=1)).replace(minute=now.minute, second=0, microsecond=0)

        future_timestamps = [next_hour + timedelta(hours=i) for i in range(hours)]
        
        # Imprime los timestamps futuros
        for ft in future_timestamps:
            print(f"Future timestamp: {ft}")

        future_timestamps_seconds = np.array([dt.timestamp() for dt in future_timestamps]).reshape(-1, 1)
        print(f"Future timestamps in seconds: {future_timestamps_seconds}")

        predicted_temperatures = self.model.predict(future_timestamps_seconds)
        print(f"Predicted temperatures: {predicted_temperatures}")

        results = []
        for ts, temp in zip(future_timestamps_seconds, predicted_temperatures):
            predicted_time = pd.to_datetime(ts[0], unit='s', utc=True)  # Asegúrate de que esté en UTC
            predicted_time_local = predicted_time.tz_convert('America/Mexico_City')  # Ajusta la zona horaria local
            results.append({
                "timestamp": predicted_time_local.isoformat(),
                "predicted_temperature": temp
            })
        logging.info("Future temperatures solicited.")

        return results



    def close(self):
        self.client.close()