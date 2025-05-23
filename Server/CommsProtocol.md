# Client-Server Communication Protocol
the client server communication we're using is socket based protocol, which means the server and client just send
bytes to one another, therefore, we need to create a format for the communication.
The format can change overtime, so we'll send the format each time a connection is established with a client.

## The format
There should be a basic format that will extend for each command individually.

## The id
Every client request will have id for response identification.

## Push notification
An update the server send to a client.

# Encryption
The protocol should be encrypted, therefore, we'll use rsa encryption for the protocol.
At the beginning of the connection, the client will send his public key to the server and the server will reply with his public key.



> [!Note]
> The protocol should contain keys for encryption and tokens. This is something to be thinking on.

## Basic client protocol
```json
{
    "Id": "<Any>",
    "Command": "<String>",
    "Data": "<Json>",
    "Checksum": "<String>"
}
```

## Basic server protocol
```json
{
    "Id?": "<Any>",
    "StatusCode": "<Number>",
    "Status": "<String>",
    "Data": {
        "Msg": "<String>",
        ...
    },
    "Checksum": "<String>"
}
```

## Basic server push notification
```json
{
  "Update": "<String>",
  "Data?": "<Json>",
  "Checksum": "<String>"
}
```

## Register
Register a new user to the system.

#### The client request

```json
{
    "Command": "Register",
    "Data": {
        "Username": "<String>",
        "Password": "<String>"
    },
    "Checksum": "<String>"
}
```

#### The server response in case username or password are missing.

```json
{
    "StatusCode": 400,
    "Status": "Bad Request",
    "Data": {
        "Msg": "Missing Username or Password attribute."
    },
    "Checksum": "<String>"
}
```

#### The server response if username is not unique.

```json
{
    "StatusCode": 409,
    "Status": "Conflict",
    "Data": {
        "Msg": "Username must be unique."
    },
    "Checksum": "<String>"
}
```

#### The server response on successful registration.

```json
{
  "StatusCode": 201,
  "Status": "Created",
  "Data": {
    "Msg": "User registered."
  },
  "Token": "<TOKEN_HERE>",
  "Friends": [["<FRIENDS_HERE>"], ["<REQUESTS_HERE>"]],
  "Checksum": "<String>"
}
```

## Login
Login to account.

#### The client request

```json
{
  "Command": "Login",
  "Data": {
    "Username": "<String>",
    "Password": "<String>"
  },
  "Checksum": "<String>"
}
```

#### The server response in case the username or the password are missing.

```json
{
  "StatusCode": 400,
  "Status": "Bad Request",
  "Data": {
    "Msg": "Missing Username or Password attribute."
  },
  "Checksum": "<String>"
}
```

#### The server response in case the user doesn't exist

```json
{
  "StatusCode": 404,
  "Status": "Not Found",
  "Data": {
    "Msg": "Invalid Credentials."
  },
  "Checksum": "<String>"
}
```

#### The server response on successful login.

```json
{
  "StatusCode": 202,
  "Status": "Accepted",
  "Data": {
    "Msg": "Logged in successfully."
  },
  "Token": "<TOKEN_HERE>",
  "Friends": [["<FRIENDS_HERE>"], ["<REQUESTS_HERE>"]],
  "Checksum": "<String>"
}
```

---

## Auth
From here the user have a token therefore token is required for auth.
The auth will use a token and username to identify the user request.
The username is to prevent bruteforce of the token.

---

### The server response in case the user doesn't provide auth token
```json
{
  "StatusCode": 400,
  "Status": "Bad Request",
  "Data": {
    "Msg": "No Token provided."
  },
  "Checksum": "<String>"
}
```

## Create Lobby
Create a new sudoku lobby.

### The client request

```json
{
  "Command": "Create_Lobby",
  "Data": {},
  "Token": "<TOKEN_HERE>",
  "Username": "<USERNAME_HERE>",
  "Checksum": "<String>"
}
```

### The server response in case the user is already in lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User already in lobby."
  },
  "Checksum": "<String>"
}
```

### The server response on successfully creating the lobby
```json
{
  "StatusCode": 201,
  "Status": "Created",
  "Data": {
    "Msg": "Lobby created successfully.",
    "Lobby_Info": {
      ...
    },
    "Checksum": "<String>"
  }
}
```

## Join Lobby (Using code)
Join a lobby using code.

### The clint request
```json
{
  "Command": "Create_Lobby",
  "Data": {
    "Code": "<Number>"
  },
  "Token": "<TOKEN_HERE>",
  "Username": "<USERNAME_HERE>",
  "Checksum": "<String>"
}
```

### The server response in case the user is already in lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User already in lobby."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user doesn't provide code
```json
{
  "StatusCode": 400,
  "Status": "Bad Request",
  "Data": {
    "Msg": "No Code provided."
  },
  "Checksum": "<String>"
}
```

### The server response in case the code is invalid
```json
{
  "StatusCode": 404,
  "Status": "Not Found",
  "Data": {
    "Msg": "Invalid Code."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user is blocked from the server

```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "You're blocked from the lobby."
  },
  "Checksum": "<String>"
}
```
### The server response on successfully joining the lobby
```json
{
    "StatusCode": 200,
    "Status": "OK",
    "Data": {
    "Msg": "Successfully joining lobby.",
    "Lobby_Info": {
      ...
    },
    "Role": "<String>"
    },
    "Checksum": "<String>"
}
```

### The server push notification to all the user in the lobby
```json
{
    "Update": "User_Joined_Lobby",
    "Data": {
    "Msg": "New user joined the lobby.",
    "Username": "<String>",
    "Role": "<String>"
    },
    "Checksum": "<String>"
}
```

## Leave Lobby
Leave a lobby the user inside.

### The clint request
```json
{
    "Command": "Leave_Lobby",
    "Data": {},
    "Token": "<TOKEN_HERE>",
    "Username": "<USERNAME_HERE>",
    "Checksum": "<String>"
}
```

### The server response in case the user isn't in lobby
```json
{
    "StatusCode": 409,
    "Status": "Conflict",
    "Data": {
    "Msg": "User isn't in lobby."
    },
    "Checksum": "<String>"
}
```

### The server response on successfully leaving the lobby
```json
{
    "StatusCode": 200,
    "Status": "OK",
    "Data": {
    "Msg": "Successfully leaving lobby."
    },
    "Checksum": "<String>"
}
```

### The server push notification to all the clients in the lobby
```json
{
    "Update": "User_Left_Lobby",
    "Data": {
    "Username": "<USERNAME_HERE>",
    "Role": "<ROLE_HERE>"
    },
    "Checksum": "<String>"
}
```

## Become Lobby Spectator
Become a spectator in lobby (players only)

### The client request
```json
{
    "Command": "Become_Lobby_Spectator",
    "Data": {},
    "Token": "<TOKEN_HERE>",
    "Username": "<USERNAME_HERE>",
    "Checksum": "<String>"
}
```

### The server response in case the user isn't in lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User isn't in lobby."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user isn't a player
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User is already a spectator."
  },
  "Checksum": "<String>"
}
```

### The server response on successfully becoming a spectator
```json
{
  "StatusCode": 200,
  "Status": "OK",
  "Data": {
    "Msg": "Successfully becoming a spectator."
  },
  "Checksum": "<String>"
}
```

### The server push notification to all the clients in the lobby when user became a spectator
```json
{
  "Update": "Become_Spectator",
  "Data": {
    "Username": "<USERNAME_HERE>"
  },
  "Checksum": "<String>"
}
```

## Become Lobby Player
Become a player in lobby (spectators only)

### The client request
```json
{
  "Command": "Become_Lobby_Player",
  "Data": {},
  "Token": "<TOKEN_HERE>",
  "Checksum": "<String>"
}
```

### The server response in case the user isn't in lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User isn't in lobby."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user isn't a player
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User is already a player."
  },
  "Checksum": "<String>"
}
```

### The server response in case the lobby is full

```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "The lobby is full."
  },
  "Checksum": "<String>"
}
```

### The server response on successfully becoming a player
```json
{
  "StatusCode": 200,
  "Status": "OK",
  "Data": {
    "Msg": "Successfully becoming a player."
  },
  "Checksum": "<String>"
}
```

### The server response on successfully becoming a player
```json
{
  "StatusCode": 200,
  "Status": "OK",
  "Data": {
    "Msg": "Successfully becoming a player."
  },
  "Checksum": "<String>"
}
```

### The server push notification to all the clients in the lobby when user became a player
```json
{
  "Update": "Become_Player",
  "Data": {
    "Username": "<USERNAME_HERE>"
  },
  "Checksum": "<String>"
}
```

## Make Lobby Spectator
Make a lobby player to a spectator, lobby owner only.

### The client request
```json
{
  "Command": "Make_Lobby_Spectator",
  "Data": {
    "Username": "<USERNAME_HERE>"
  },
  "Token": "<TOKEN_HERE>",
  "Checksum": "<String>"
}
```

### The server response in case the user (sending the request) isn't in lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User isn't in lobby."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user (sending the request) isn't the owner of the lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User isn't the owner of lobby."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user doesn't provide username
```json
{
  "StatusCode": 400,
  "Status": "Bad Request",
  "Data": {
    "Msg": "No username provided."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user (requested) isn't in the lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "Requested user isn't in lobby."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user (requested) isn't a player
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "Requested User is already a spectator."
  },
  "Checksum": "<String>"
}
```

### The server response on successfully making a spectator
```json
{
  "StatusCode": 200,
  "Status": "OK",
  "Data": {
    "Msg": "Successfully making a spectator."
  },
  "Checksum": "<String>"
}
```

### The server push notification to all the clients in the lobby when user became a spectator
```json
{
  "Update": "Become_Spectator",
  "Data": {
    "Username": "<USERNAME_HERE>"
  },
  "Checksum": "<String>"
}
```

## Get Lobby
Get information about lobby using code.

### The clint request
```json
{
  "Command": "Get_Lobby",
  "Data": {},
  "Token": "<TOKEN_HERE>",
  "Checksum": "<String>"
}
```

### The server response in case the user doesn't provide code
```json
{
  "StatusCode": 400,
  "Status": "Bad Request",
  "Data": {
    "Msg": "No code provided."
  },
  "Checksum": "<String>"
}
```

### The server response in case the code is invalid
```json
{
  "StatusCode": 404,
  "Status": "Not Found",
  "Data": {
    "Msg": "Invalid code."
  },
  "Checksum": "<String>"
}
```

### The server response on successfully joining the lobby
```json
{
  "StatusCode": 200,
  "Status": "OK",
  "Data": {
    "Lobby_Info": {
      ...
    }
  },
  "Checksum": "<String>"
}
```

### The server push notification to all the clients in the lobby when user joined
```json
{
  "Update": "User_Joined_Lobby",
  "Data": {},
  "Checksum": "<String>"
}
```

## Kick User Lobby
kick a user from a lobby, only the owner can kick a player.

### The clint request
```json
{
  "Command": "Kick_User_Lobby",
  "Data": {
    "Username": "<String>"
  },
  "Token": "<TOKEN_HERE>",
  "Checksum": "<String>"
}
```

### The server response in case the user isn't in lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User isn't in lobby."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user isn't the owner of the lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User isn't the owner of lobby."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user doesn't provide username
```json
{
  "StatusCode": 400,
  "Status": "Bad Request",
  "Data": {
    "Msg": "No username provided."
  },
  "Checksum": "<String>"
}
```

### The server response in case the username is invalid
```json
{
  "StatusCode": 404,
  "Status": "Not Found",
  "Data": {
    "Msg": "Invalid username."
  },
  "Checksum": "<String>"
}
```

### The serer response in case the user to kick is not inside the lobby
```json
{
  "StatusCode": 404,
  "Status": "Not Found",
  "Data": {
    "Msg": "User to kick isn't in lobby."
  },
  "Checksum": "<String>"
}
```

### The server response on successfully kicking the user
```json
{
  "StatusCode": 200,
  "Status": "OK",
  "Data": {
    "Msg": "User kicked."
  },
  "Checksum": "<String>"
}
```

### The server push notification to the kicked user on kick
```json
{
  "Update": "Lobby_Kick",
  "Data": {
    "Msg": "You have been kicked from the lobby."
  },
  "Checksum": "<String>"
}
```

## Ban User Lobby
Ban a user from a lobby, only the owner can ban a player.

### The clint request
```json
{
  "Command": "Ban_User_Lobby",
  "Data": {
    "Username": "<String>"
  },
  "Token": "<TOKEN_HERE>",
  "Checksum": "<String>"
}
```

### The server response in case the user isn't in lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User isn't in lobby."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user isn't the owner of the lobby
```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "User isn't the owner of lobby."
  },
  "Checksum": "<String>"
}
```

### The server response in case the user doesn't provide username
```json
{
  "StatusCode": 400,
  "Status": "Bad Request",
  "Data": {
    "Msg": "No username provided."
  },
  "Checksum": "<String>"
}
```

### The server response in case the username is invalid
```json
{
  "StatusCode": 404,
  "Status": "Not Found",
  "Data": {
    "Msg": "Invalid username."
  },
  "Checksum": "<String>"
}
```

### The serer response in case the user to ban is not inside the lobby
```json
{
  "StatusCode": 404,
  "Status": "Not Found",
  "Data": {
    "Msg": "User to ban isn't in lobby."
  },
  "Checksum": "<String>"
}
```

### The server response on successfully kicking the user
```json
{
  "StatusCode": 200,
  "Status": "OK",
  "Data": {
    "Msg": "User baned."
  },
  "Checksum": "<String>"
}
```

### The server push notification to the baned user on kick
```json
{
  "Update": "Lobby_Ban",
  "Data": {
    "Msg": "You have been baned from the lobby."
  },
  "Checksum": "<String>"
}
```

### The server push notification to all the clients in the lobby
```json
{
  "Update": "User_Left_Lobby",
  "Data": {
    "Username": "<USERNAME_HERE>",
    "Role": "Player"
  },
  "Checksum": "<String>"
}
```

## Add Friend
add friend

### The clint request
```json
{
  "Command": "Add_Friend",
  "Data": {
    "Username": "<String>"
  },
  "Token": "<TOKEN_HERE>",
  "Checksum": "<String>"
}
```

### The server response in case the user doesn't provide username
```json
{
  "StatusCode": 400,
  "Status": "Bad Request",
  "Data": {
    "Msg": "No username provided."
  },
  "Checksum": "<String>"
}
```

### The server response in case the username is invalid
```json
{
  "StatusCode": 404,
  "Status": "Not Found",
  "Data": {
    "Msg": "Invalid username."
  },
  "Checksum": "<String>"
}
```

### The server response on successfully sending friend request
```json
{
  "StatusCode": 200,
  "Status": "OK",
  "Data": {
    "Msg": "Friend request sent."
  },
  "Checksum": "<String>"
}
```

### The server push notification to the requested user
```json
{
  "Update": "Friend_Request",
  "Data": {
    "Username": "<USERNAME_HERE>"
  },
  "Checksum": "<String>"
}
```

## Accept Friend
accept friend request.

## Reject Friend
reject friend request.

## Remove Friend
remove friend.

## Start Game
start a game in the lobby (owner only).

## Game Move
make a move in the game.

### The clint request
```json
{
  "Command": "Game_Move",
  "Data": {
    "Move": {
        "row": "<Number>",
        "column": "<Number>",
        "value": "<Number>"
    }
  },
  "Token": "<TOKEN_HERE>",
  "Checksum": "<String>"
}
```

