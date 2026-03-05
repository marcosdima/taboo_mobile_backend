from app.extensions import db
from app.models import Group, Member, Plays


def create_user_and_token(client, alias, password="password123"):
    user_response = client.post("/users", json={"alias": alias, "password": password})
    user = user_response.get_json()

    login_response = client.post("/login", json={"alias": alias, "password": password})
    token = login_response.get_json()["token"]
    return user, token


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_group(game_id, name):
    group = Group(game_id=game_id, name=name)
    db.session.add(group)
    db.session.commit()
    return group


def get_group_by_name(game_id, name):
    return Group.query.filter_by(game_id=game_id, name=name).first()


class TestGroupAssignmentsRoutes:
    def test_post_assign_success_when_requester_is_player(self, client):
        game_response = client.post("/games", json={})
        game_id = game_response.get_json()["id"]

        target_user, target_token = create_user_and_token(client, "group_target_user")
        client.post(
            "/play",
            json={"user_id": target_user["id"], "game_id": game_id},
            headers=auth_headers(target_token),
        )

        group = get_group_by_name(game_id, "Blue")

        response = client.post(
            "/groups/assignments",
            json={"user_id": target_user["id"], "group_id": group.id},
        )

        assert response.status_code == 201
        payload = response.get_json()
        assert payload["group_id"] == group.id
        assert payload["game_id"] == game_id
        assert payload["play_id"] is not None

        target_play = Plays.query.filter_by(user_id=target_user["id"], game_id=game_id).first()
        assert target_play is not None
        assert payload["play_id"] == target_play.id


    def test_post_assign_fails_when_requester_not_player(self, client):
        game_id = client.post("/games", json={}).get_json()["id"]
        target_user, target_token = create_user_and_token(client, "target_not_player")

        client.post(
            "/play",
            json={"user_id": target_user["id"], "game_id": game_id},
            headers=auth_headers(target_token),
        )

        outsider_user, outsider_token = create_user_and_token(client, "outsider_user")
        assert outsider_user["id"] != target_user["id"]

        group = get_group_by_name(game_id, "Red")

        response = client.post(
            "/groups/assignments",
            json={"user_id": target_user["id"], "group_id": group.id},
            headers=auth_headers(outsider_token),
        )

        assert response.status_code == 403
        assert response.get_json()["error"] == "Only players in this game can assign groups"


    def test_post_assign_is_unique_per_game(self, client):
        game_id = client.post("/games", json={}).get_json()["id"]
        user, token = create_user_and_token(client, "unique_group_user")

        client.post(
            "/play",
            json={"user_id": user["id"], "game_id": game_id},
            headers=auth_headers(token),
        )

        group_a = create_group(game_id, "Team A")
        group_b = create_group(game_id, "Team B")

        first = client.post(
            "/groups/assignments",
            json={"user_id": user["id"], "group_id": group_a.id},
        )
        second = client.post(
            "/groups/assignments",
            json={"user_id": user["id"], "group_id": group_b.id},
        )

        assert first.status_code == 201
        assert second.status_code == 400
        assert second.get_json()["error"] == "User already assigned in this game. Use PUT to update"


    def test_put_reassign_success_for_creator(self, client):
        game_id = client.post("/games", json={}).get_json()["id"]
        user, token = create_user_and_token(client, "reassign_user")

        client.post(
            "/play",
            json={"user_id": user["id"], "game_id": game_id},
            headers=auth_headers(token),
        )

        group_a = create_group(game_id, "Alpha")
        group_b = create_group(game_id, "Beta")

        assign_response = client.post(
            "/groups/assignments",
            json={"user_id": user["id"], "group_id": group_a.id},
        )
        assert assign_response.status_code == 201

        reassign_response = client.put(
            "/groups/assignments",
            json={"user_id": user["id"], "group_id": group_b.id},
        )

        assert reassign_response.status_code == 200
        assert reassign_response.get_json()["group_id"] == group_b.id


    def test_put_reassign_fails_for_non_creator(self, client):
        game_id = client.post("/games", json={}).get_json()["id"]
        user, token = create_user_and_token(client, "non_creator_target")

        client.post(
            "/play",
            json={"user_id": user["id"], "game_id": game_id},
            headers=auth_headers(token),
        )

        non_creator, non_creator_token = create_user_and_token(client, "non_creator_actor")
        client.post(
            "/play",
            json={"user_id": non_creator["id"], "game_id": game_id},
            headers=auth_headers(non_creator_token),
        )

        group_a = create_group(game_id, "Gamma")
        group_b = create_group(game_id, "Delta")

        assign_response = client.post(
            "/groups/assignments",
            json={"user_id": user["id"], "group_id": group_a.id},
        )
        assert assign_response.status_code == 201

        reassign_response = client.put(
            "/groups/assignments",
            json={"user_id": user["id"], "group_id": group_b.id},
            headers=auth_headers(non_creator_token),
        )

        assert reassign_response.status_code == 403
        assert reassign_response.get_json()["error"] == "Only game creator can reassign groups"


    def test_post_assign_fails_when_user_not_playing_in_game(self, client):
        game_id = client.post("/games", json={}).get_json()["id"]
        user, _ = create_user_and_token(client, "not_playing_user")
        group = create_group(game_id, "Oranges")

        response = client.post(
            "/groups/assignments",
            json={"user_id": user["id"], "group_id": group.id},
        )

        assert response.status_code == 400
        assert response.get_json()["error"] == "User must be playing in this game"


    def test_put_reassign_requires_existing_assignment(self, client):
        game_id = client.post("/games", json={}).get_json()["id"]
        user, token = create_user_and_token(client, "needs_assignment_first")

        client.post(
            "/play",
            json={"user_id": user["id"], "game_id": game_id},
            headers=auth_headers(token),
        )

        group = create_group(game_id, "No Assignment Yet")

        response = client.put(
            "/groups/assignments",
            json={"user_id": user["id"], "group_id": group.id},
        )

        assert response.status_code == 404
        assert response.get_json()["error"] == "User has no group assignment in this game"


    def test_post_assign_rejects_group_from_other_game(self, client):
        game1_id = client.post("/games", json={}).get_json()["id"]

        user, token = create_user_and_token(client, "cross_game_user")
        client.post(
            "/play",
            json={"user_id": user["id"], "game_id": game1_id},
            headers=auth_headers(token),
        )

        creator2, creator2_token = create_user_and_token(client, "creator_second_game")
        game2_response = client.post("/games", json={}, headers=auth_headers(creator2_token))
        game2_id = game2_response.get_json()["id"]

        other_game_group = create_group(game2_id, "Other Game Group")

        response = client.post(
            "/groups/assignments",
            json={"user_id": user["id"], "group_id": other_game_group.id},
        )

        assert response.status_code == 403
        assert response.get_json()["error"] == "Only players in this game can assign groups"

        member = Member.query.first()
        assert member is None


    def test_get_groups_with_members_by_game(self, client):
        game_id = client.post("/games", json={}).get_json()["id"]

        user1, token1 = create_user_and_token(client, "member_one")
        user2, token2 = create_user_and_token(client, "member_two")

        client.post(
            "/play",
            json={"user_id": user1["id"], "game_id": game_id},
            headers=auth_headers(token1),
        )
        client.post(
            "/play",
            json={"user_id": user2["id"], "game_id": game_id},
            headers=auth_headers(token2),
        )

        group_a = create_group(game_id, "Red Team")
        group_b = create_group(game_id, "Blue Team")

        client.post(
            "/groups/assignments",
            json={"user_id": user1["id"], "group_id": group_a.id},
        )
        client.post(
            "/groups/assignments",
            json={"user_id": user2["id"], "group_id": group_b.id},
        )

        response = client.get(f"/groups/{game_id}")

        assert response.status_code == 200
        groups = response.get_json()
        assert len(groups) == 4

        red_team = next(g for g in groups if g["name"] == "Red Team")
        blue_team = next(g for g in groups if g["name"] == "Blue Team")

        assert len(red_team["members"]) == 1
        assert len(blue_team["members"]) == 1
        assert red_team["members"][0]["group_id"] == group_a.id
        assert blue_team["members"][0]["group_id"] == group_b.id

        default_red = next(g for g in groups if g["name"] == "Red")
        default_blue = next(g for g in groups if g["name"] == "Blue")
        assert default_red["members"] == []
        assert default_blue["members"] == []


    def test_get_groups_empty_when_no_members(self, client):
        game_id = client.post("/games", json={}).get_json()["id"]

        response = client.get(f"/groups/{game_id}")

        assert response.status_code == 200
        groups = response.get_json()
        assert len(groups) == 2
        assert all(group["members"] == [] for group in groups)


    def test_get_groups_returns_default_groups(self, client):
        game_id = client.post("/games", json={}).get_json()["id"]

        response = client.get(f"/groups/{game_id}")

        assert response.status_code == 200
        groups = response.get_json()
        assert len(groups) == 2
        assert sorted([group["name"] for group in groups]) == ["Blue", "Red"]
        assert all(group["members"] == [] for group in groups)


    def test_get_groups_fails_for_nonexistent_game(self, client):
        response = client.get("/groups/99999")

        assert response.status_code == 404
        assert response.get_json()["error"] == "Game not found"
