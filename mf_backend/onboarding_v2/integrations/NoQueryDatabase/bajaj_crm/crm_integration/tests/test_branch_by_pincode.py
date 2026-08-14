from unittest.mock import patch


def test_branch_by_pincode_success(api_client):
    payload = {"pincode": "121004"}
    expected_data = [
        {"branch_code": "BR001", "branch_name": "Faridabad Main Branch"},
        {"branch_code": "BR002", "branch_name": "Faridabad Sector 15 Branch"}
    ]

    with patch('crm_integration.views.MasterUseCase') as MockMasterUseCase:
        mock_usecase = MockMasterUseCase.return_value
        mock_usecase.get_branches_by_pincode.return_value = {
            "StatusCode": 200,
            "Message": "Branches fetched successfully",
            "Data": expected_data
        }

        response = api_client.post('/api/branches/by-pincode/', data=payload, format='json')

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Branches fetched successfully",
        "data": expected_data
    }


def test_branch_by_pincode_no_branches(api_client):
    payload = {"pincode": "999999"}

    with patch('crm_integration.views.MasterUseCase') as MockMasterUseCase:
        mock_usecase = MockMasterUseCase.return_value
        mock_usecase.get_branches_by_pincode.return_value = {
            "StatusCode": 404,
            "Message": "No branches found for the given pincode",
            "Data": []
        }

        response = api_client.post('/api/branches/by-pincode/', data=payload, format='json')

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "message": "No branches found for the given pincode",
        "data": []
    }


def test_branch_by_pincode_missing_pincode(api_client):
    response = api_client.post('/api/branches/by-pincode/', data={}, format='json')

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "Invalid pincode",
        "data": []
    }


def test_branch_by_pincode_invalid_pincode(api_client):
    response = api_client.post('/api/branches/by-pincode/', data={"pincode": "12A004"}, format='json')

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "Invalid pincode",
        "data": []
    }
