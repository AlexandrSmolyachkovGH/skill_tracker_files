from file_service.msg_creator import msg_creator


def test_msg_creator() -> None:
    root_title = msg_creator.get_root_title()
    root_description = msg_creator.get_root_description()

    assert root_title.startswith("Skill Tracker")
    assert root_description.startswith("REST API")
