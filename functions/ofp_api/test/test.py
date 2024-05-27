import os
import sys


os.environ['DB_HOST'] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ['DB_NAME'] = "ofp"
os.environ['DB_USER'] = "postgres"
os.environ['DB_PASSWORD'] = "postgres"
os.environ['STAGE'] = ''
os.environ['REGION'] = 'us-east-1'

test_dir = os.path.dirname(__file__)
function_dir = os.path.normpath(os.path.join(test_dir, '../'))

sys.path.append(function_dir)


import app
import uvicorn
if __name__ == "__main__":
    uvicorn.run(app.app, host="0.0.0.0", port=8000)
    