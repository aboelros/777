import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from fastapi import status
from io import BytesIO

from app.main import app as app_instance
from app.db.models import User, Project, ProjectMember, ProjectRole, Product
from app.core.database import AsyncSessionLocal
from app.core.security import get_current_user_id

pytestmark = pytest.mark.asyncio

async def setup_test_data(db):
    user_a = User(id=uuid4(), email=f'user_a_{uuid4()}@example.com', password_hash='pw', is_active=True)
    user_b = User(id=uuid4(), email=f'user_b_{uuid4()}@example.com', password_hash='pw', is_active=True)
    user_c = User(id=uuid4(), email=f'user_c_{uuid4()}@example.com', password_hash='pw', is_active=True)

    db.add_all([user_a, user_b, user_c])
    await db.commit()

    project_a = Project(id=uuid4(), owner_id=user_a.id, name='Project A', project_code=str(uuid4())[:8])
    project_b = Project(id=uuid4(), owner_id=user_b.id, name='Project B', project_code=str(uuid4())[:8])
    db.add_all([project_a, project_b])
    await db.commit()

    member_a = ProjectMember(id=uuid4(), project_id=project_a.id, user_id=user_a.id, role=ProjectRole.OWNER.value)
    member_b = ProjectMember(id=uuid4(), project_id=project_b.id, user_id=user_b.id, role=ProjectRole.OWNER.value)
    db.add_all([member_a, member_b])
    await db.commit()

    product_a = Product(
        id=uuid4(), project_id=project_a.id, name="Product A", price=10.0, in_stock=True
    )
    product_b = Product(
        id=uuid4(), project_id=project_b.id, name="Product B", price=20.0, in_stock=True
    )
    db.add_all([product_a, product_b])
    await db.commit()

    return {
        "user_a": user_a, "project_a": project_a, "product_a": product_a,
        "user_b": user_b, "project_b": project_b, "product_b": product_b,
        "user_c": user_c
    }

@pytest.fixture
async def env():
    async with AsyncSessionLocal() as db:
        data = await setup_test_data(db)
    yield data
    # Cleanup overrides if any
    app_instance.dependency_overrides.clear()

@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app_instance, client=('127.0.0.1', 1234), raise_app_exceptions=True), base_url='http://test')

# 1. Same-tenant access: User A can access authorized Project A resources.
async def test_tenant_a_can_list_own_products(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.get(f'/api/v1/products/{env["project_a"].id}')
    assert resp.status_code in [200, 201]
    data = resp.json()
    assert len(data["products"]) == 1
    assert data["products"][0]["name"] == "Product A"

# 2. Same-tenant creation: User A can create in Project A
async def test_tenant_a_can_create_product(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.post(
        f'/api/v1/products/{env["project_a"].id}',
        json={"name": "New Prod A", "price": 15.0}
    )
    assert resp.status_code in [200, 201]
    assert resp.json()["message"] == "Product created successfully"

# 3. Same-tenant update: User A can update their product
async def test_tenant_a_can_update_product(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.put(
        f'/api/v1/products/{env["project_a"].id}/{env["product_a"].id}',
        json={"name": "Updated Prod A", "price": 99.0}
    )
    assert resp.status_code in [200, 201]

# 4. Same-tenant delete: User A can delete their product
async def test_tenant_a_can_delete_product(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.delete(f'/api/v1/products/{env["project_a"].id}/{env["product_a"].id}')
    assert resp.status_code in [200, 204]

# 5. Cross-tenant read: User A cannot read Project B's list
async def test_tenant_a_cannot_list_tenant_b_products(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.get(f'/api/v1/products/{env["project_b"].id}')
    assert resp.status_code in [403, 404]

# 6. Cross-tenant read: User A cannot read Project B's specific product
async def test_tenant_a_cannot_get_tenant_b_product(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.get(f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}')
    assert resp.status_code in [403, 404]

# 7. Cross-tenant update: User A cannot alter Project B's product
async def test_tenant_a_cannot_update_tenant_b_product(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.put(
        f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}',
        json={"name": "Hacked", "price": 0}
    )
    assert resp.status_code in [403, 404]

# 8. Cross-tenant delete: User A cannot delete Project B's product
async def test_tenant_a_cannot_delete_tenant_b_product(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.delete(f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}')
    assert resp.status_code in [403, 404]

# 9. Forged Project ID: User A passing Project B's ID in URL for creation
async def test_forged_project_id_in_product_create_rejected(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.post(
        f'/api/v1/products/{env["project_b"].id}',
        json={"name": "Forged Prod", "price": 1.0}
    )
    assert resp.status_code in [403, 404]

# 10. Mutation Isolation: Project B's product is unchanged after failed cross-tenant update
async def test_mutation_isolation_on_cross_tenant_attack(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.put(
        f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}',
        json={"name": "Hacked", "price": 0}
    )
    assert resp.status_code in [403, 404]

    # Verify B's product is unchanged using User B's identity
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_b"].id)
    resp_check = await client.get(f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}')
    assert resp_check.status_code == 200
    assert resp_check.json()["name"] == "Product B"

# 11. Missing Auth: Fails closed
async def test_missing_authentication_fails_closed(env, client):
    app_instance.dependency_overrides.clear()
    resp = await client.get(f'/api/v1/products/{env["project_a"].id}')
    assert resp.status_code == 401

# 12. Cross-tenant bulk upload denied
async def test_cross_tenant_bulk_upload_denied(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    csv_content = b"name,price\nBulk Prod,10\n"
    resp = await client.post(
        f'/api/v1/products/{env["project_b"].id}/bulk-upload',
        files={"file": ("test.csv", csv_content, "text/csv")}
    )
    assert resp.status_code in [403, 404]

# 13. Same-tenant media access: User A can upload about photos
async def test_tenant_a_can_upload_about_photos(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.post(
        f'/api/v1/projects/{env["project_a"].id}/about/photos',
        files={"photos": ("t.jpg", b"fake_image_data", "image/jpeg")}
    )
    assert resp.status_code in [200, 201]

# 14. Cross-tenant media upload denied
async def test_cross_tenant_upload_about_photos_denied(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.post(
        f'/api/v1/projects/{env["project_b"].id}/about/photos',
        files={"photos": ("t.jpg", b"fake_image_data", "image/jpeg")}
    )
    assert resp.status_code in [403, 404]

# 15. Cross-tenant media delete denied
async def test_cross_tenant_delete_about_photos_denied(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.delete(f'/api/v1/projects/{env["project_b"].id}/about/photos')
    assert resp.status_code in [403, 404]

# 16. Cross-tenant storage read denied
async def test_cross_tenant_storage_read_denied(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.get(f'/api/v1/storage/images/products/{env["project_b"].id}/secret.jpg')
    assert resp.status_code in [403, 404]

# 17. Cross-tenant product image upload denied
async def test_cross_tenant_product_image_upload_denied(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_b"].id)
    initial_images = (await client.get(f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}')).json().get("images", [])
    if initial_images is None:
        initial_images = []

    import os
    from app.services.file_storage import UPLOAD_DIR
    proj_dir = UPLOAD_DIR / str(env["project_b"].id)
    initial_files = set(os.listdir(proj_dir)) if proj_dir.exists() else set()

    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.post(
        f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}/images',
        files={"file": ("t.jpg", b"fake_data", "image/jpeg")}
    )
    assert resp.status_code in [403, 404]

    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_b"].id)
    final_images = (await client.get(f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}')).json().get("images", [])
    if final_images is None:
        final_images = []

    assert initial_images == final_images
    final_files = set(os.listdir(proj_dir)) if proj_dir.exists() else set()
    assert initial_files == final_files

# 18. Cross-tenant product image delete denied
async def test_cross_tenant_product_image_delete_denied(env, client):
    # First ensure B has an image to delete
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_b"].id)
    resp = await client.post(
        f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}/images',
        files={"file": ("b.jpg", b"fake_data", "image/jpeg")}
    )
    if resp.status_code != 200:
        print("ERROR RESPONSE:", resp.json())
    assert resp.status_code in [200, 201]
    initial_images = (await client.get(f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}')).json().get("images", [])
    assert len(initial_images) >= 1

    import os
    from app.services.file_storage import UPLOAD_DIR
    proj_dir = UPLOAD_DIR / str(env["project_b"].id)
    initial_files = set(os.listdir(proj_dir)) if proj_dir.exists() else set()

    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.delete(
        f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}/images/0'
    )
    assert resp.status_code in [403, 404]

    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_b"].id)
    final_images = (await client.get(f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}')).json().get("images", [])

    assert initial_images == final_images
    final_files = set(os.listdir(proj_dir)) if proj_dir.exists() else set()
    assert initial_files == final_files

# 19. Cross-tenant product image update denied
async def test_cross_tenant_update_product_image_denied(env, client):
    # Setup: B uploads an image
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_b"].id)
    await client.post(
        f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}/images',
        files={"file": ("b.jpg", b"fake_data", "image/jpeg")}
    )
    initial_images = (await client.get(f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}')).json().get("images", [])
    assert len(initial_images) >= 1

    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    resp = await client.patch(
        f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}/images/0',
        params={"description": "Hacked desc", "order": 1}
    )
    assert resp.status_code in [403, 404]

    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_b"].id)
    final_images = (await client.get(f'/api/v1/products/{env["project_b"].id}/{env["product_b"].id}')).json().get("images", [])

    assert initial_images == final_images

# 20. Same-tenant media access: User A can get about photos
async def test_tenant_a_can_get_about_photos(env, client):
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    await client.post(
        f'/api/v1/projects/{env["project_a"].id}/about/photos',
        files={"photos": ("t.jpg", b"fake_image_data", "image/jpeg")}
    )
    resp = await client.get(f'/api/v1/projects/{env["project_a"].id}/about/photos')
    assert resp.status_code in [200, 201]

# 21. Cross-tenant media get denied/isolated
async def test_cross_tenant_get_about_photos_denied(env, client):
    # Setup B's photo
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_b"].id)
    await client.post(
        f'/api/v1/projects/{env["project_b"].id}/about/photos',
        files={"photos": ("b.jpg", b"fake_b", "image/jpeg")}
    )

    # Setup A's photo
    app_instance.dependency_overrides[get_current_user_id] = lambda: str(env["user_a"].id)
    await client.post(
        f'/api/v1/projects/{env["project_a"].id}/about/photos',
        files={"photos": ("a.jpg", b"fake_a", "image/jpeg")}
    )

    # A requests B's project route
    resp = await client.get(f'/api/v1/projects/{env["project_b"].id}/about/photos')

    # TenantContext natively rejects forged project IDs with 403 or 404
    assert resp.status_code in [403, 404]

    # Verify A can still see only A's photo
    resp_a = await client.get(f'/api/v1/projects/{env["project_a"].id}/about/photos')
    assert resp_a.status_code == 200
    urls = [p["url"] for p in resp_a.json().get("photos", [])]
    assert len(urls) > 0
    # Confirm B's project_id does not appear in any of A's URLs
    for url in urls:
        assert str(env["project_b"].id) not in url
