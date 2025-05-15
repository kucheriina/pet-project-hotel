from decimal import Decimal

import pytest
from dateutil.parser import isoparse
from rest_framework.test import APIClient
from catalog.models import Room


@pytest.mark.django_db
class TestRoomViewSet:
    def setup_method(self):
        self.client = APIClient()

    # --- CREATE ROOM TESTS ---

    def test_create_room_success(self):
        data = {
            "room_class": "economy",
            "bed_type": "1",
            "price_per_night": "1200.00",
            "description": "Бюджетный номер"
        }
        response = self.client.post("/catalog/create/", data, format='json')
        assert response.status_code == 201
        assert "room_id" in response.data
        assert Room.objects.count() == 1

    @pytest.mark.parametrize("data,missing_field", [
        ({  # Нет bed_type
            "room_class": "standard",
            "price_per_night": "2000.00",
            "description": "Стандартный номер"
        }, "bed_type"),
        ({  # Нет room_class
            "bed_type": "2",
            "price_per_night": "2000.00",
            "description": "Стандартный номер"
        }, "room_class"),
        ({  # Нет description
            "room_class": "lux",
            "bed_type": "family",
            "price_per_night": "3000.00",
        }, "description"),
        ({  # Нет price_per_night
            "room_class": "economy",
            "bed_type": "1",
            "description": "Недорогой номер"
        }, "price_per_night"),
    ])
    def test_create_room_missing_fields(self, data, missing_field):
        response = self.client.post("/catalog/create/", data, format='json')
        assert response.status_code == 400
        assert missing_field in response.data

    @pytest.mark.parametrize('invalid_price, expected_error', [
        ("-100.00", "Ensure this value is greater than or equal to 0."),
        ("abc", "A valid number is required."),
        ("", "A valid number is required."),
        (None, "This field may not be null.")
    ])
    def test_create_room_invalid_price(self, invalid_price, expected_error):
        data = {
            "room_class": "standard",
            "bed_type": "2",
            "price_per_night": invalid_price,
            "description": "Некорректная цена"
        }
        response = self.client.post("/catalog/create/", data, format='json')
        assert response.status_code == 400
        assert "price_per_night" in response.data
        assert expected_error in response.data["price_per_night"][0]

    # --- DELETE ROOM TESTS ---

    def test_delete_room_success(self):
        room = Room.objects.create(
            room_class="lux", bed_type="family",
            price_per_night=5000.00, description="VIP номер"
        )
        response = self.client.delete(f"/catalog/{room.id}/delete/")
        assert response.status_code == 200
        assert Room.objects.count() == 0

    def test_delete_room_not_found(self):
        response = self.client.delete("/catalog/9999/delete/")
        assert response.status_code == 404

    # --- LIST ROOMS TESTS ---

    def test_list_rooms_unsorted(self):
        Room.objects.create(room_class="economy", bed_type="1", price_per_night=1000, description="Эконом")
        Room.objects.create(room_class="standard", bed_type="2", price_per_night=3000, description="Стандарт")
        response = self.client.get("/catalog/list/")
        assert response.status_code == 200
        assert 'results' in response.data
        assert len(response.data['results']) == 2

    @pytest.mark.parametrize("sort_by,order", [
        ("price_per_night", "asc"),
        ("price_per_night", "desc"),
        ("created_at", "asc"),
        ("created_at", "desc"),
    ])
    def test_list_rooms_sorted(self, sort_by, order):
        Room.objects.create(room_class="economy", bed_type="1", price_per_night=1000, description="Эконом")
        Room.objects.create(room_class="standard", bed_type="2", price_per_night=3000, description="Стандарт")
        response = self.client.get(f"/catalog/list/?sort_by={sort_by}&order={order}")
        assert response.status_code == 200
        assert 'results' in response.data
        rooms = response.data['results']
        assert len(rooms) == 2

        if sort_by == 'price_per_night':
            values = [Decimal(room['price_per_night']) for room in rooms]
        elif sort_by == 'created_at':
            values = [isoparse(room['created_at']) for room in rooms]
        else:
            values = []

        expected = sorted(values, reverse=(order == 'desc'))
        assert values == expected, f'Expected {order} sort_by {sort_by}, got {values}'

    def test_list_rooms_invalid_sort_field(self):
        response = self.client.get("/catalog/list/?sort_by=wrong_field")
        assert response.status_code == 400
        assert "Неверный параметр сортировки" in response.data["detail"]

    def test_list_rooms_invalid_sort_order(self):
        response = self.client.get("/catalog/list/?sort_by=price_per_night&order=sideways")
        assert response.status_code == 400
        assert "Неверный параметр порядка сортировки" in response.data["detail"]

    def test_list_rooms_pagination(self):
        for i in range(15):
            Room.objects.create(room_class='economy', bed_type='1', price_per_night=1000 + i, description=f'Room {i}')

        response = self.client.get('/catalog/list/?page=1')
        assert response.status_code == 200
        assert 'results' in response.data
        assert len(response.data['results']) == 10
        assert response.data['count'] == 15
        assert response.data['next'] is not None
        assert response.data['previous'] is None

        response_page_2 = self.client.get("/catalog/list/?page=2")
        assert response_page_2.status_code == 200
        assert len(response_page_2.data['results']) == 5
        assert response_page_2.data['count'] == 15
        assert response_page_2.data['next'] is None
        assert response_page_2.data['previous'] is not None

    def test_list_rooms_pagination_invalid_page(self):
        for i in range(5):
            Room.objects.create(room_class="economy", bed_type="1", price_per_night=1000 + i, description=f"Room {i}")

        response = self.client.get('/catalog/list/?page=999')
        assert response.status_code == 404
        assert 'Invalid page' in str(response.data) or 'Page not found' in str(response.data)