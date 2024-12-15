# Database Rules
The json database doesn't have a build in system for table rules,
unlike sql based database. And so we think of the rules and implement them individually.

## User System
All the user account related databases.

* uid (userid) is unique
* username is unique

### Basic user data on users.json

```json
{
  "<username>": {
    "password": <Hashed password>,
    "salt": <Hashed password salt>,
    "last_login": <Date>
    ...
  }
}
```