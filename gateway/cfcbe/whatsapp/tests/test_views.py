import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_whatsapp_webhook_view(client):
    url = reverse('whatsapp_webhook')  # Assuming 'whatsapp_webhook' is the name of your view
    data = {'key': 'value'}  # Replace this with the actual data that your webhook expects
    response = client.post(url, data=data, content_type='application/json')
    
    # Adjust this assertion based on the expected response
    assert response.status_code == 200
    assert 'expected_field' in response.json()

@pytest.mark.django_db
def test_get_test_case(client):
    # Replace with the actual URL for the "get test case" view
    url = reverse('get_test_case')  # Example URL name
    response = client.get(url)
    
    # Adjust assertions based on expected behavior
    assert response.status_code == 200
    assert 'test_case_data' in response.json()

@pytest.mark.django_db
def test_create_test_case(client):
    url = reverse('create_test_case')  # Replace with actual URL name for the view
    data = {
        'name': 'Test Case 1',
        'description': 'Description of Test Case 1',
        'priority': 'High'
    }
    response = client.post(url, data=data, content_type='application/json')
    
    # Adjust the assertion based on your expected response
    assert response.status_code == 201  # Created status code
    assert 'id' in response.json()

@pytest.mark.django_db
def test_update_test_case(client):
    # Assuming you have a test case with ID 1 that you're trying to update
    url = reverse('update_test_case', args=[1])  # Replace with the actual update URL pattern
    data = {
        'name': 'Updated Test Case',
        'description': 'Updated description',
        'priority': 'Medium'
    }
    response = client.put(url, data=data, content_type='application/json')
    
    assert response.status_code == 200
    assert response.json()['name'] == 'Updated Test Case'

@pytest.mark.django_db
def test_delete_test_case(client):
    # Replace with the actual URL name for deleting a test case
    url = reverse('delete_test_case', args=[1])  # Replace with the actual test case ID
    response = client.delete(url)
    
    assert response.status_code == 204  # No content after deletion

# Add more tests as needed based on your views
