from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config.settings import MONGODB_URI, DATABASE_NAME


def connect_mongodb(mongo_uri: str = None, db_name: str = None):
    """
    Kết nối MongoDB
    
    Args:
        mongo_uri: MongoDB connection string (optional)
        db_name: Tên database (optional)
        
    Returns:
        (client, db) tuple
        
    Raises:
        ConnectionFailure: Nếu không thể kết nối
    """
    uri = mongo_uri or MONGODB_URI
    db_name = db_name or DATABASE_NAME
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        
        db = client[db_name]
        print(f"✓ Kết nối thành công đến MongoDB: {db_name}")
        return client, db
    except ConnectionFailure as e:
        print(f"✗ Lỗi kết nối MongoDB: {e}")
        raise
    except Exception as e:
        print(f"✗ Lỗi không xác định: {e}")
        raise


def close_mongodb(client):
    """
    Đóng kết nối MongoDB
    
    Args:
        client: MongoClient instance
    """
    if client:
        client.close()
        print("✓ Đã đóng kết nối MongoDB")


def test_connection(mongo_uri: str = None) -> bool:
    """
    Test kết nối MongoDB
    
    Args:
        mongo_uri: MongoDB connection string
        
    Returns:
        True nếu kết nối thành công
    """
    try:
        client, db = connect_mongodb(mongo_uri)
        close_mongodb(client)
        return True
    except:
        return False
