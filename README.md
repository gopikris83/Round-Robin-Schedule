# Round Robin Rotation Schedule

This is repo is to fetch members from Slack user group like **Digital & IT Tech Leads** and rotate through the list to, for example schedule the hosting of the Tech Lead Forum with the members of this group.


## How it works

This rotation schedule can be reused to any other rotation schedule use case by small customization. In order to reuse the rotation schedule, following customization has to be done.
  - Create a new Github action workflow (Existing workflow that rotates every bi-weekly based on the requirements for tech lead forum) and this workflow can be created to work weekly or monthly or daily using cronjob schedule given on workflow.
  - Key inputs are needed to rotate and send notification to slack channel (passed as Global ENV in the workflow).
    - Input the Slack Group (this will fetch the slack groups members dynamically when there is addition or removal of members in the group).
    - Input the channel id for sending notification
    - Input the file suffix (This will create a new file and add all the members included in the rotation by fetching through slack group)
    - Currently, the message body is not set as dynamic and this can be changed in the python script so that messages can be fed in the ENV parameters of the Github workflow created for every use cases.
    - Invite SAS-Round-Robin App to your channel to get the notification schedule.

That's it. The workflow should start to schedule the rotation!
