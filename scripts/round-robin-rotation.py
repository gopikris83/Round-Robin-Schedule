import json
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_TOKEN = os.getenv("SLACK_TOKEN")  # Slack Bot Token
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")  # Slack Channel ID
SLACK_USER_GROUP = os.getenv("SLACK_USER_GROUP")  # Slack User Group Name
MESSAGE_BODY = os.getenv("MESSAGE_BODY")  # Message to send to Slack
MESSAGE_BODY_NEXT = os.getenv("MESSAGE_BODY_NEXT")  # Message to send to the next person in rotation
FILE_SUFFIX = os.getenv("FILE_SUFFIX")  # File suffix for the JSON file

client = WebClient(token=SLACK_TOKEN)

# Team members list and rotation file
ROTATION_FILE = f"jsons/rotation_members_{FILE_SUFFIX}.json"

def load_team_members():
    """Load team members and current rotation state from a file."""
    try:
        if not os.path.isfile(ROTATION_FILE):
            with open(ROTATION_FILE, "w") as f:
                f.write("{}")
                data = {"members": [], "current_index": 0}
        else:
            with open(ROTATION_FILE, "r") as f:
                data = json.load(f)
    except FileNotFoundError:
        data = {"members": [], "current_index": 0}
        save_team_members(data)
    except json.JSONDecodeError:
        # File exists but contains invalid JSON
        raise ValueError(f"The file {ROTATION_FILE} contains invalid JSON.")
    return data

def save_team_members(data):
    """Save team members and current rotation state to a file."""
    if not os.path.isfile(ROTATION_FILE):
        with open(ROTATION_FILE, "w") as f:
            f.write("{}")
            json.dump(data, f, indent=4)
    else:
        print(f"File already exists: {ROTATION_FILE}")
        with open(ROTATION_FILE, "w") as f:
            json.dump(data, f, indent=4)

# Get the next member in the rotation and update the state
def get_next_rotation():
    """Get the next member in the rotation and update the state."""
    data = load_team_members()
    members = data["members"]
    current_index = data["current_index"]

    next_index = (current_index + 1) % len(members)
    second_next_index = (current_index + 2) % len(members)

    next_member = members[next_index]
    second_next_member = members[second_next_index]

    # Update the rotation index
    data["current_index"] = next_index
    save_team_members(data)

    return next_member, second_next_member

# Send a notification to Slack
def notify_slack(next_member, second_next_member):
    """Send a notification to Slack."""
    client = WebClient(token=SLACK_TOKEN)
    rotation_filename = os.path.basename(ROTATION_FILE)
    
    try:
        message = (
            f"Hej <@{next_member['id']}> :wave:, {MESSAGE_BODY}\n"
            f" \n"
            f"🔄 Heads up, <@{second_next_member['id']}> {MESSAGE_BODY_NEXT}"
            f" You can check the rotation schedule <https://github.com/flysas-tech/round-robin-rotation-schedule/blob/main/jsons/{rotation_filename}|here>."
          )
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]
        response = client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        print("Notification sent:", response["ts"])
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Fetch the ID of a user group by its name
def get_user_group_id_by_name(group_name):
    """
    Fetch the ID of a user group by its name.
    """
    try:
        response = client.usergroups_list()
        user_groups = response.get("usergroups", [])

        # Create a mapping of names to IDs
        group_map = {group["name"]: group["id"] for group in user_groups}

        if group_name in group_map:
            return group_map[group_name]
        else:
            print(f"User group with name '{group_name}' not found.")
            return None

    except SlackApiError as e:
        print(f"Error fetching user groups: {e.response['error']}")
        return None
    
# Fetch all members of a user group by its name
def fetch_user_group_members_by_name(group_name):
    """
    Fetch all members of a user group by its name.
    """
    user_group_id = get_user_group_id_by_name(group_name)
    if not user_group_id:
        return

    try:
        response = client.usergroups_users_list(usergroup=user_group_id)
        members = response.get("users", [])

        data = load_team_members()        
        current_index = data["current_index"]

        if members:
            member_data = []
            for index, member in enumerate(members, start=1):
                member_name = fetch_user_info(member)
                member_data.append({"name": member_name, "id": member})

            # Construct JSON Output
            output = {
                "members": member_data,
                "current_index": current_index
            }

            print(json.dumps(output, indent=4))
            save_team_members(output)
            return output
        else:
            print(f"No members found for User Group '{group_name}'.")

    except SlackApiError as e:
        print(f"Error fetching user group members: {e.response['error']}")

# Fetch the name of a user by their ID
def fetch_user_info(user_id):
    """
    Fetch the name of a user by their ID.
    """
    try:
        response = client.users_info(user=user_id)
        user = response.get("user", {})
        return user.get("name")
    except SlackApiError as e:
        print(f"Error fetching user info for {user_id}: {e.response['error']}")
        return None

def main():
    """Main function to handle rotation and notification."""
     # Input the name of the user group
    group_name = SLACK_USER_GROUP
    fetch_user_group_members_by_name(group_name)
    next_member, second_next_member = get_next_rotation()
    notify_slack(next_member, second_next_member)

if __name__ == "__main__":
    main()
