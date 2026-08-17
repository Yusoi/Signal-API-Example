from uuid import uuid4


async def test_create_flag_success(client):
    response = await client.post(
        "/flags",
        json={"key": "new-flag", "name": "New Flag", "is_active": True},
    )

    assert response.status_code == 200
    flag_id = response.json()
    assert flag_id

    get_response = await client.get("/flags/new-flag")
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["id"] == flag_id
    assert body["key"] == "new-flag"
    assert body["name"] == "New Flag"
    assert body["is_active"] is True


async def test_create_flag_invalid_key_returns_422(client):
    response = await client.post(
        "/flags",
        json={"key": "No Good Key!", "name": "Bad Flag", "is_active": True},
    )

    assert response.status_code == 422


async def test_create_flag_duplicate_key_currently_errors(client):
    body = {"key": "dup-flag", "name": "Dup Flag", "is_active": True}

    first = await client.post("/flags", json=body)
    assert first.status_code == 200

    second = await client.post("/flags", json=body)

    # Characterization test: duplicate keys aren't handled by the controller
    # (src/flags/controllers/flags.py) so the IntegrityError propagates unhandled.
    assert second.status_code == 500


async def test_get_flag_success(client, seed_flag):
    await seed_flag("existing-flag", name="Existing", is_active=False)

    response = await client.get("/flags/existing-flag")

    assert response.status_code == 200
    body = response.json()
    assert body["key"] == "existing-flag"
    assert body["name"] == "Existing"
    assert body["is_active"] is False


async def test_get_flag_not_found_returns_404(client):
    response = await client.get("/flags/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Flag does not exist"}


async def test_patch_flag_toggles_global_state(client, seed_flag):
    await seed_flag("toggle-flag", is_active=False)

    patch_response = await client.patch("/flags/toggle-flag", params={"is_active": True})
    assert patch_response.status_code == 200

    get_response = await client.get("/flags/toggle-flag")
    assert get_response.json()["is_active"] is True


async def test_patch_flag_nonexistent_key_is_silent_noop(client):
    response = await client.patch("/flags/does-not-exist", params={"is_active": True})

    # Characterization test: the UPDATE affects 0 rows and no error is raised.
    assert response.status_code == 200


async def test_get_user_access_no_override_returns_global(client, seed_flag):
    await seed_flag("access-flag", is_active=True)
    user_id = uuid4()

    response = await client.get(f"/flags/access-flag/users/{user_id}")

    assert response.status_code == 200
    assert response.json() is True


async def test_get_user_access_flag_not_found_returns_404(client):
    response = await client.get(f"/flags/does-not-exist/users/{uuid4()}")

    assert response.status_code == 404


async def test_patch_user_override_creates_and_is_reflected(client, seed_flag):
    await seed_flag("override-flag", is_active=False)
    user_id = uuid4()

    patch_response = await client.patch(
        f"/flags/override-flag/users/{user_id}", params={"is_active": True}
    )
    assert patch_response.status_code == 200

    access_response = await client.get(f"/flags/override-flag/users/{user_id}")
    assert access_response.json() is True


async def test_patch_user_override_upserts_on_second_call(client, seed_flag):
    await seed_flag("upsert-flag", is_active=False)
    user_id = uuid4()

    await client.patch(f"/flags/upsert-flag/users/{user_id}", params={"is_active": True})
    await client.patch(f"/flags/upsert-flag/users/{user_id}", params={"is_active": False})

    access_response = await client.get(f"/flags/upsert-flag/users/{user_id}")
    assert access_response.json() is False
