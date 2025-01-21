import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_env_variables():
    """Load environment variables from .env file"""
    try:
        load_dotenv()
        required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        return True
    except Exception as e:
        logger.error(f"Error loading environment variables: {str(e)}")
        return False

def get_database_url():
    """Construct database URL from environment variables"""
    try:
        port = os.getenv('DB_PORT', '5432')  # Default to 5432 if not specified
        db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{port}/{os.getenv('DB_NAME')}"
        return db_url
    except Exception as e:
        logger.error(f"Error constructing database URL: {str(e)}")
        return None

def get_db_connection():
    """Create and return a database connection"""
    try:
        if not load_env_variables():
            raise Exception("Failed to load environment variables")
            
        db_url = get_database_url()
        if not db_url:
            raise Exception("Failed to construct database URL")
            
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return None

def load_table_to_df(table_name, engine=None):
    """Load a specific table into a pandas DataFrame"""
    try:
        if engine is None:
            engine = get_db_connection()
            
        if engine is None:
            raise Exception("Failed to establish database connection")
            
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(text(query), engine)
        logger.info(f"Successfully loaded table: {table_name}")
        return df
    except Exception as e:
        logger.error(f"Error loading table {table_name}: {str(e)}")
        return None

def execute_query(query, engine=None):
    """Execute a custom SQL query and return results as a DataFrame"""
    try:
        if engine is None:
            engine = get_db_connection()
            
        if engine is None:
            raise Exception("Failed to establish database connection")
            
        df = pd.read_sql_query(text(query), engine)
        logger.info("Query executed successfully")
        return df
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return None

# Example usage:
if __name__ == "__main__":
    # Test database connection
    engine = get_db_connection()
    if engine:
        try:
            # Test connection by getting table names
            with engine.connect() as conn:
                query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                result = conn.execute(query)
                tables = [row[0] for row in result]
                logger.info(f"Available tables: {tables}")
        except Exception as e:
            logger.error(f"Error testing connection: {str(e)}")