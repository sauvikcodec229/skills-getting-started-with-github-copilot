"""
Comprehensive tests for Mergington High School API using TestClient with AAA pattern.

Tests cover:
- Root endpoint and redirects
- Getting all activities
- Signing up for activities
- Unregistering from activities
- Error handling and edge cases
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient instance for testing."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for varsity and JV levels",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and practice tennis skills on the school courts",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and acting workshops",
            "schedule": "Mondays, Wednesdays, Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["jacob@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Compete in debates and develop public speaking skills",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore STEM concepts through hands-on projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(initial_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(initial_activities)


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_redirect_to_static(self, client):
        """Test that root endpoint redirects to static HTML."""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
    
    def test_root_follow_redirect(self, client):
        """Test that root endpoint can be followed to static HTML."""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert response.status_code == 200


class TestGetActivities:
    """Tests for getting all activities."""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test getting all activities returns correct data."""
        # Arrange - Activities are reset by fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_structure(self, client, reset_activities):
        """Test that activities have correct structure."""
        # Arrange - Activities are reset by fixture
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_contains_participants(self, client, reset_activities):
        """Test that activities include their participants."""
        # Arrange - Activities are reset by fixture
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 2
    
    def test_get_activities_content_type(self, client, reset_activities):
        """Test that response has correct content type."""
        # Arrange - Activities are reset by fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.headers["content-type"] == "application/json"


class TestSignupForActivity:
    """Tests for signing up for activities."""
    
    def test_signup_new_student(self, client, reset_activities):
        """Test signing up a new student for an activity."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_student_added_to_activity(self, client, reset_activities):
        """Test that student is actually added to activity participants."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Programming Class"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        activities_data = response.json()
        assert email in activities_data[activity_name]["participants"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test signing up multiple students increases participant count."""
        # Arrange
        activity_name = "Gym Class"
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        
        # Act
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        for email in emails:
            client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count + len(emails)
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test that signing up for non-existent activity returns 404."""
        # Arrange
        email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signup returns 400."""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_preserves_existing_participants(self, client, reset_activities):
        """Test that signup doesn't remove existing participants."""
        # Arrange
        activity_name = "Tennis Club"
        new_email = "newsignup@mergington.edu"
        existing_emails = ["lucas@mergington.edu", "ava@mergington.edu"]
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for email in existing_emails + [new_email]:
            assert email in participants
    
    def test_signup_different_activities_independent(self, client, reset_activities):
        """Test that signups for different activities are independent."""
        # Arrange
        email = "testuser@mergington.edu"
        signup_activity = "Chess Club"
        other_activities = ["Gym Class", "Drama Club"]
        
        # Act
        client.post(
            f"/activities/{signup_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        data = response.json()
        assert email in data[signup_activity]["participants"]
        for activity in other_activities:
            assert email not in data[activity]["participants"]
    
    def test_signup_response_format(self, client, reset_activities):
        """Test that signup response has correct format."""
        # Arrange
        email = "test@mergington.edu"
        activity_name = "Debate Team"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)


class TestUnregisterParticipant:
    """Tests for unregistering participants from activities."""
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant."""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant."""
        # Arrange
        email_to_remove = "emma@mergington.edu"
        activity_name = "Programming Class"
        remaining_email = "sophia@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert email_to_remove not in participants
        assert remaining_email in participants
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from non-existent activity returns 404."""
        # Arrange
        email = "student@mergington.edu"
        nonexistent_activity = "Fake Club"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_nonexistent_participant(self, client, reset_activities):
        """Test unregistering non-existent participant returns 404."""
        # Arrange
        nonexistent_email = "notmember@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]
    
    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregistering multiple participants one by one."""
        # Arrange
        activity_name = "Tennis Club"
        emails_to_remove = ["lucas@mergington.edu", "ava@mergington.edu"]
        
        # Act
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        for email in emails_to_remove:
            client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count - len(emails_to_remove)
    
    def test_unregister_twice_fails(self, client, reset_activities):
        """Test that unregistering the same participant twice fails."""
        # Arrange
        email = "alex@mergington.edu"
        activity_name = "Basketball Team"
        
        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
    
    def test_unregister_response_format(self, client, reset_activities):
        """Test that unregister response has correct format."""
        # Arrange
        email = "jacob@mergington.edu"
        activity_name = "Drama Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)


class TestIntegrationScenarios:
    """Integration tests for common workflows."""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering."""
        # Arrange
        student = "tempstudent@mergington.edu"
        activity_name = "Art Studio"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student}
        )
        
        # Assert - Verify signed up
        assert signup_response.status_code == 200
        get_response = client.get("/activities")
        assert student in get_response.json()[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/participants/{student}"
        )
        
        # Assert - Verify unregistered
        assert unregister_response.status_code == 200
        final_response = client.get("/activities")
        assert student not in final_response.json()[activity_name]["participants"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test same student signing up for multiple activities."""
        # Arrange
        student = "multiactivity@mergington.edu"
        activities_list = ["Chess Club", "Debate Team", "Science Club"]
        
        # Act
        for activity in activities_list:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": student}
            )
            assert response.status_code == 200
        
        # Assert
        get_response = client.get("/activities")
        data = get_response.json()
        for activity in activities_list:
            assert student in data[activity]["participants"]
    
    def test_concurrent_signups_different_students(self, client, reset_activities):
        """Test multiple students signing up for the same activity."""
        # Arrange
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        activity_name = "Science Club"
        
        # Act
        for student in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student}
            )
            assert response.status_code == 200
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for student in students:
            assert student in participants
