"""Unit tests for myskoda.driving_range."""

from pathlib import Path
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest

from myskoda import RestApi
from myskoda.auth.authorization import Authorization
from myskoda.models.driving_range import EngineType

FIXTURES_DIR = Path(__file__).parent.joinpath("fixtures")


print(f"__file__ = {__file__}")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("fixture_file", "expected_values"),
    [
        (
            "superb/driving-range-car-type-hybrid.json",
            {
                "car_type": EngineType.HYBRID,
                "primary_engine": EngineType.GASOLINE,
                "expected_primary_range": 670,
                "secondary_engine": EngineType.ELECTRIC,
                "expected_secondary_range": 7,
            },
        ),
        (
            "enyaq/driving-range-iv80-car-type-electric.json",
            {
                "car_type": EngineType.ELECTRIC,
                "primary_engine": EngineType.ELECTRIC,
                "expected_primary_range": 139,
            },
        ),
    ],
)
async def test_get_driving_range(
    fixture_file: str, expected_values: dict[str, dict[str, EngineType | int]]
) -> None:
    """Test case for driving range response."""
    vehicle_status = FIXTURES_DIR.joinpath(fixture_file).read_text()
    response_mock = AsyncMock()
    response_mock.text.return_value = vehicle_status
    session_mock = MagicMock()
    session_mock.get.return_value.__aenter__.return_value = response_mock

    authorization = Authorization(session_mock)
    api = RestApi(session_mock, authorization)
    api.authorization.get_access_token = AsyncMock()
    target_vin = "TMBJM0CKV1N12345"
    get_status_result = await api.get_driving_range(target_vin)

    assert get_status_result.car_type == expected_values["car_type"]
    assert get_status_result.primary_engine_range.engine_type == expected_values["primary_engine"]
    assert (
        get_status_result.primary_engine_range.remaining_range_in_km
        == expected_values["expected_primary_range"]
    )
    if get_status_result.secondary_engine_range is not None:
        assert (
            get_status_result.secondary_engine_range.engine_type
            == expected_values["secondary_engine"]
        )
        assert (
            get_status_result.secondary_engine_range.remaining_range_in_km
            == expected_values["expected_secondary_range"]
        )

    session_mock.get.assert_called_with(
        f"https://mysmob.api.connect.skoda-auto.cz/api/v2/vehicle-status/{target_vin}/driving-range",
        headers=ANY,
    )
