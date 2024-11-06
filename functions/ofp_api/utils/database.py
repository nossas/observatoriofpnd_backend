from sqlalchemy import create_engine, text as sqlalchemy_text
from sqlalchemy.pool import NullPool
from string import Template
import pandas as pd


def execute_sql_script(db_uri, script):
    """
    Executes a SQL script containing potentially multiple statements. This function is designed 
    for operations where only the execution success is relevant, and not the return of any result.
    Useful for data modifications and schema changes where outputs are not needed.

    Parameters:
        db_uri (str): Database connection URI.
        script (str): SQL script containing one or more SQL commands.

    Returns:
        bool: True if the script executes successfully, otherwise it raises an exception.
    """
    try:
        engine = create_engine(db_uri, poolclass=NullPool, connect_args={'connect_timeout': 45})
        with engine.connect().execution_options(autocommit=True) as conn:
            with conn.begin():
                conn.execute(sqlalchemy_text(script))
            conn.close()
        return True
    except Exception as e:
        raise e


def execute_query(db_uri, query):
    """
    Executes a SQL query and returns the results formatted as a list of dictionaries,
    where keys are column names. This function is particularly useful for API interactions
    that require data retrieval in a structured format suitable for JSON serialization.

    Parameters:
        db_uri (str): Database connection URI.
        query (str): SQL query to be executed.

    Returns:
        list[dict]: Results of the query as a list of dictionaries, allowing for easy further processing.
    """
    try:
        engine = create_engine(db_uri, poolclass=NullPool, connect_args={'connect_timeout': 45})
        with engine.connect().execution_options(autocommit=True) as conn:
            result = conn.execute(sqlalchemy_text(query))
            if result.cursor:
                rows = result.cursor.fetchall()
                column_names = [i.name for i in result.cursor.description]
                result = [dict(zip(column_names, row)) for row in rows]
            conn.close()
        return result
    except Exception as e:
        raise e


def execute_query_to_dataframe(db_uri, query):
    """
    Executes a SQL query using pandas' read_sql_query and returns the DataFrame
    with the index set to the first column.

    Parameters:
        db_uri (str): Database connection URI.
        query (str): SQL query to be executed.

    Returns:
        DataFrame: Results of the query as a pandas DataFrame, with the index set to the first column.
    """
    try:
        # Criar um engine SQLAlchemy para conectar ao banco de dados
        engine = create_engine(db_uri, poolclass=NullPool, connect_args={'connect_timeout': 45})

        # Executar a consulta e retornar o resultado como um DataFrame
        df = pd.read_sql_query(sqlalchemy_text(query), engine)

        # Definir a primeira coluna do DataFrame como índice
        if not df.empty:
            df = df.set_index(df.columns[0])

        # Fechar a conexão
        engine.dispose()

        return df
    except Exception as e:
        raise e


def sql_replace_params(query, params={}):
    """
    Replaces placeholders in a SQL query with actual values from a dictionary, handling None values appropriately.
    This function uses string templates for substitution, and explicitly converts Python's None to SQL's null.

    Parameters:
        query (str): The SQL query template with placeholders.
        params (dict): A dictionary mapping placeholders to their respective values.

    Returns:
        str: The query with all placeholders substituted and None values replaced with SQL null.
    """
    query = Template(query).safe_substitute(params)
    query = query.replace("'None'", 'null')  # Replace string representations of None
    query = query.replace('None', 'null')    # Replace None in other contexts
    return query
