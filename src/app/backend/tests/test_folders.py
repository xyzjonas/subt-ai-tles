from collections.abc import Callable

from fastapi.testclient import TestClient

from tests.conftest import FakeQueue
from tests.test_api import _finish, _upload
from tests.test_summaries import recognized  # noqa: F401


def _folder(client: TestClient, auth: tuple[str, str], name: str) -> dict:
    r = client.post("/api/folders", json={"name": name}, auth=auth)
    assert r.status_code == 201, r.text
    return r.json()


def _ids(client: TestClient, auth: tuple[str, str], **params: object) -> list[str]:
    r = client.get("/api/jobs", params=params, auth=auth)
    return [job["id"] for job in r.json()]


def test_folder_crud(client: TestClient, make_user: Callable) -> None:
    fran = make_user("fran")
    folder = _folder(client, fran, "  Shows   2026 ")
    assert folder["name"] == "Shows 2026"

    dup = client.post("/api/folders", json={"name": "shows 2026"}, auth=fran)
    assert dup.status_code == 409
    assert dup.json()["code"] == "folder_name_taken"

    renamed = client.patch(f"/api/folders/{folder['id']}", json={"name": "Cartoons"}, auth=fran)
    assert renamed.json()["name"] == "Cartoons"
    assert [f["name"] for f in client.get("/api/folders", auth=fran).json()] == ["Cartoons"]

    assert client.delete(f"/api/folders/{folder['id']}", auth=fran).status_code == 204
    assert client.get("/api/folders", auth=fran).json() == []


def test_folders_are_private(client: TestClient, make_user: Callable) -> None:
    owner, other = make_user("owner"), make_user("other")
    folder = _folder(client, owner, "Mine")
    job = _upload(client, other)

    assert client.get("/api/folders", auth=other).json() == []
    assert client.delete(f"/api/folders/{folder['id']}", auth=other).status_code == 404
    r = client.patch(f"/api/jobs/{job['id']}", json={"folderId": folder["id"]}, auth=other)
    assert r.status_code == 404
    assert r.json()["code"] == "folder_not_found"


def test_job_moves_between_folders(client: TestClient, make_user: Callable) -> None:
    mona = make_user("mona")
    folder = _folder(client, mona, "Anime")
    job = _upload(client, mona)
    assert "folderId" not in job

    r = client.patch(f"/api/jobs/{job['id']}", json={"folderId": folder["id"]}, auth=mona)
    assert r.json()["folderId"] == folder["id"]

    # an update without folderId leaves the folder alone
    r = client.patch(f"/api/jobs/{job['id']}", json={"archived": False}, auth=mona)
    assert r.json()["folderId"] == folder["id"]

    r = client.patch(f"/api/jobs/{job['id']}", json={"folderId": None}, auth=mona)
    assert "folderId" not in r.json()


def test_deleting_a_folder_keeps_its_jobs(client: TestClient, make_user: Callable) -> None:
    dina = make_user("dina")
    folder = _folder(client, dina, "Temp")
    job = _upload(client, dina)
    client.patch(f"/api/jobs/{job['id']}", json={"folderId": folder["id"]}, auth=dina)

    client.delete(f"/api/folders/{folder['id']}", auth=dina)
    kept = client.get(f"/api/jobs/{job['id']}", auth=dina).json()
    assert "folderId" not in kept


def test_archive_hides_job_but_keeps_it_reachable(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    arno = make_user("arno")
    job_id = _upload(client, arno)["id"]

    # a running translation can't be archived
    r = client.patch(f"/api/jobs/{job_id}", json={"archived": True}, auth=arno)
    assert r.status_code == 409
    assert r.json()["code"] == "job_still_processing"

    _finish(client, queue, arno, job_id)
    r = client.patch(f"/api/jobs/{job_id}", json={"archived": True}, auth=arno)
    assert r.json()["archivedAt"]

    assert _ids(client, arno) == []
    assert _ids(client, arno, archived=True) == [job_id]
    assert client.get(f"/api/jobs/{job_id}", auth=arno).status_code == 200
    assert client.get(f"/api/jobs/{job_id}/download", auth=arno).status_code == 200

    r = client.patch(f"/api/jobs/{job_id}", json={"archived": False}, auth=arno)
    assert "archivedAt" not in r.json()
    assert _ids(client, arno) == [job_id]
    assert _ids(client, arno, archived=True) == []


def test_recognized_episodes_are_grouped_by_show(
    client: TestClient,
    make_user: Callable,
    queue: FakeQueue,
    recognized: None,  # noqa: ARG001, F811
) -> None:
    tess = make_user("tess")
    first, second = _upload(client, tess)["id"], _upload(client, tess)["id"]
    queue.run_all()

    folders = client.get("/api/folders", auth=tess).json()
    assert [f["name"] for f in folders] == ["The Office"]
    for job_id in (first, second):
        job = client.get(f"/api/jobs/{job_id}", auth=tess).json()
        assert job["folderId"] == folders[0]["id"]


def test_recognition_respects_a_manual_folder(
    client: TestClient,
    make_user: Callable,
    queue: FakeQueue,
    recognized: None,  # noqa: ARG001, F811
) -> None:
    manu = make_user("manu")
    mine = _folder(client, manu, "Mine")
    job_id = _upload(client, manu)["id"]
    client.patch(f"/api/jobs/{job_id}", json={"folderId": mine["id"]}, auth=manu)

    job = _finish(client, queue, manu, job_id)
    assert job["folderId"] == mine["id"]


def test_unrecognized_files_stay_ungrouped(
    client: TestClient, make_user: Callable, queue: FakeQueue
) -> None:
    una = make_user("una")
    job = _finish(client, queue, una, _upload(client, una)["id"])
    assert "folderId" not in job
    assert client.get("/api/folders", auth=una).json() == []
