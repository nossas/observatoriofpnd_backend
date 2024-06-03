from database import execute_sql_script, sql_replace_params
import os

PATH = 'utils/'
PG_URI = "postgresql://{user}:{password}@{host}:{port}/{name}".format(
    name=os.environ['DB_NAME'],
    host=os.environ['DB_HOST'],
    port=os.environ['DB_PORT'],
    user=os.environ['DB_ADMIN_USER'],
    password=os.environ['DB_ADMIN_PASSWORD'])


SUBSTITUTIONS = {
    "DB_SOLUTION_USER": os.environ['DB_SOLUTION_USER'],
    "DB_SOLUTION_USER_PASSWORD": os.environ['DB_SOLUTION_USER_PASSWORD'],
}


def lambda_handler(event, context):
    try:

        files = [os.path.join(PATH, f) for f in os.listdir(PATH) if os.path.isfile(os.path.join(PATH, f))]
        for file in files:
            print(f"Done: {file}")
            script = sql_replace_params(open(file).read(), SUBSTITUTIONS)
            execute_sql_script(PG_URI, script)

    except Exception as error:
        print(error)
        raise error
