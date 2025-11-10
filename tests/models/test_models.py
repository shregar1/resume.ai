"""
Model tests.
"""
import pytest
from datetime import datetime
from models.user import User


@pytest.mark.unit
class TestUserModel:
    """Test cases for User model."""
    
    def test_user_model_creation(self, sample_user_data):
        """Test user model can be created."""
        user = User(**sample_user_data)
        
        assert user.email == sample_user_data["email"]
        assert user.id == sample_user_data["id"]
        assert user.urn == sample_user_data["urn"]
    
    def test_user_model_attributes(self):
        """Test user model has required attributes."""
        user = User(
            id=1,
            urn="test-urn",
            email="test@example.com",
            password="hashed",
            is_logged_in=False,
            is_deleted=False,
            created_on=datetime.now()
        )
        
        assert hasattr(user, 'email')
        assert hasattr(user, 'password')
        assert hasattr(user, 'is_logged_in')
        assert hasattr(user, 'is_deleted')
        assert hasattr(user, 'created_on')

