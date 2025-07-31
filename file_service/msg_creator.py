class MsgCreator:
    def get_root_title(self) -> str:
        message = "Skill Tracker File Service"
        return message

    def get_root_description(self) -> str:
        message = "REST API for handling files related to the main Skill Tracker application"
        return message


msg_creator = MsgCreator()
