from src.price_calculator import calculate_total_price_from_shopping_list


def test_calculate_total_price_from_shopping_list():
    shopping_list = {
        "kjottdeig": {
            "estimated_total_price": 130
        },
        "ris": {
            "estimated_total_price": 35
        },
        "mais": {
            "estimated_total_price": 15
        }
    }

    total_price = calculate_total_price_from_shopping_list(shopping_list)

    assert total_price == 180