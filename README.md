# issues2cards

Pulls Github issues and creates/updates Trello cards.  Work in progress.
Implements several basic actions, leaving room to decide final functionality.

### Running

```
python3 issues2cards.py [-h] [-c <conf>]
```

-c <conf> (default `conf.yaml`) configuration file

### Configuration file

 - `repos`: list of Github repositories in `<user>/<repo>` format
 - `horizon_days`: doesn't consider issues whith `last_update` more than this number of days ago.
 - `board.id`: boardId of trello board.
 - `board.lists.new-issues`: listId to put new issue cards.
 - `board.lists.waiting`: listId for cards waiting for activity.
 - `board.lists.activity`: listId to move cards that have new activity.

### Current (minimal) functionality:

- Gathers open Github issues (PR or issue) with activity during the last `horizon_days`. (list A)
- lists all Github attachments from non-archived cards in the Trello board. (list B)
- for each issue in set(A - B), creates a new card in the `new-issues` list.
- compares the last modification timestamp of each card in the `waiting` list.
  - if the Github issue has an update later than that, moves the card to the `activity` list.

### TODOs

- Currently ignores the list of Github repos.  `Kong/kong` is hardcoded.
- if a card is moved to another board, the Github issue would be considered "new" and another card created in the `new-issues` list.
- any activity on a card in the `waiting` list would touch its "last modification" date and could skip some Github activity.
- should copy labels?  some of them?
