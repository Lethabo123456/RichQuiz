import pandas as pd
import pymysql

# ✅ Connect to your Railway-hosted MySQL database
conn = pymysql.connect(
    host="shuttle.proxy.rlwy.net",
    user="root",
    password="TyFFRLfZlxmbDydGgmVAHBXfcMrmVdXU",
    database="railway",
    port=12523
)

# ✅ Fetch data from user_performance table
query = "SELECT * FROM user_performance"
df = pd.read_sql(query, conn)

# ✅ Save as CSV for local training
output_path = "quiz_data.csv"
df.to_csv(output_path, index=False)

conn.close()
print(f"✅ Export complete! Data saved as {output_path}")
