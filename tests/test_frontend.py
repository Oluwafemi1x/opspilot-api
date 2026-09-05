def test_dashboard_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "OpsPilot" in response.text
    assert "Operations Workspace" in response.text


def test_frontend_assets_are_served(client):
    css = client.get("/app/styles.css")
    js = client.get("/app/app.js")
    assert css.status_code == 200
    assert js.status_code == 200
    assert "--accent" in css.text
    assert "const API='/api/v1'" in js.text
