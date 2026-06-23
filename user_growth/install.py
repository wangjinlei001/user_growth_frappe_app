from user_growth.mock_data import seed_mock_data


def after_install():
    seed_mock_data(record_count=200)
