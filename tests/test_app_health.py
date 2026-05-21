from adme_predictor.app_health import check_app_health, health_icon


def test_app_health_reports_required_sections():
    health = check_app_health()

    assert {"model", "molecules", "pk", "shap", "requirements", "runtime"}.issubset(health)
    assert health["molecules"]["level"] == "ok"
    assert health["pk"]["level"] == "ok"
    assert health_icon("ok") == "✅"
    assert health_icon("warn") == "⚠"
