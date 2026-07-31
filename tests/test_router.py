import pytest
from fastapi import Response

from src.core import config_settings


@pytest.fixture(scope="function")
def path_test_rate_limeter(monkeypatch):
    monkeypatch.setattr(config_settings, "all_path", True)
    monkeypatch.setattr(config_settings, "server_rm", "1/m")


def test_rate_limeter(path_test_rate_limeter, client):
    client.get("/")
    responce: Response = client.get("/")
    assert responce.status_code == 429


@pytest.fixture(scope="function")
def path_test_proxy(monkeypatch):
    monkeypatch.setattr(config_settings, "all_path", False)
    monkeypatch.setattr(config_settings, "server_rm", "1/m")


def test_proxy(path_test_proxy, client):
    for _ in range(3):
        response: Response = client.get("/")
        assert response.status_code != 429


@pytest.fixture(scope="function")
def path_test_error(monkeypatch):
    monkeypatch.setattr(config_settings, "all_path", True)
    monkeypatch.setattr(config_settings, "server_rm", "500/m")
    monkeypatch.setattr(config_settings, "server_rrm", "500/m")
    monkeypatch.setattr(config_settings, "server_max_failures", 3)
    monkeypatch.setattr(
        config_settings, "server_wait", "slow"
    )  # We don’t test server_wait=fast, as this would require adding time.sleep(), and I don’t want to make the tests slow


def test_error(path_test_error, client):
    for _ in range(3):
        response: Response = client.get("/")
        assert response.status_code != 503
    cache_response: Response = client.get("/")
    assert cache_response.status_code == 503


@pytest.fixture(scope="function")
def path_test_overload(monkeypatch):
    monkeypatch.setattr(config_settings, "all_path", True)
    monkeypatch.setattr(config_settings, "server_rm", "500/m")
    monkeypatch.setattr(config_settings, "server_rrm", "1/m")
    monkeypatch.setattr(config_settings, "server_max_wait_time", 1.5)


def test_overload(path_test_overload, client):
    client.get("/")
    cache_response: Response = client.get("/")
    assert cache_response.status_code == 429


@pytest.fixture(scope="function")
def path_test_fast_strategy(monkeypatch):
    monkeypatch.setattr(config_settings, "all_path", True)
    monkeypatch.setattr(config_settings, "server_rm", "500/m")
    monkeypatch.setattr(config_settings, "server_rrm", "500/m")
    monkeypatch.setattr(config_settings, "server_wait", "fast")


def test_fast_strategy(path_test_fast_strategy, client):
    client.get("/")
    cache_response: Response = client.get("/")
    assert cache_response.status_code == 202


@pytest.fixture(scope="function")
def path_test_slow_strategy(monkeypatch):
    monkeypatch.setattr(config_settings, "all_path", True)
    monkeypatch.setattr(config_settings, "server_rm", "500/m")
    monkeypatch.setattr(config_settings, "server_rrm", "500/m")
    monkeypatch.setattr(config_settings, "server_wait", "slow")


def test_slow_strategy(path_test_slow_strategy, client):
    client.get("/")
    cache_response: Response = client.get("/")
    assert cache_response.status_code == 504
